"""
task_manager.py — In-memory background task manager.

Spawns CLI scripts (main.py, update_tmdb.py, migrate_channel_links.py) as
subprocesses, captures stdout/stderr to log files, and tracks status.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    SCAN = "scan"
    TMDB_UPDATE = "tmdb_update"
    MIGRATION = "migration"


@dataclass
class TaskInfo:
    id: str
    task_type: TaskType
    library_id: int
    status: TaskStatus = TaskStatus.PENDING
    started_at: float = 0.0
    finished_at: float | None = None
    exit_code: int | None = None
    log_file: str = ""
    description: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "library_id": self.library_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "exit_code": self.exit_code,
            "log_file": self.log_file,
            "description": self.description,
            "extra": self.extra,
        }


# Resolve project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_LOG_DIR = _PROJECT_ROOT / "scratch" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

# Python executable — use the same one running this process
_PYTHON = sys.executable


class TaskManager:
    """Manages background subprocess tasks with log capture."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskInfo] = {}
        self._processes: dict[str, subprocess.Popen] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def launch_scan(
        self,
        library_id: int,
        telegram_channel: str,
        description: str = "",
    ) -> TaskInfo:
        """Launch main.py scraper for a specific library."""
        task_id = self._make_id("scan")
        log_path = _LOG_DIR / f"{task_id}.log"

        env_override = {
            "LIBRARY_ID": str(library_id),
            "TELEGRAM_CHANNEL": telegram_channel,
        }

        task = TaskInfo(
            id=task_id,
            task_type=TaskType.SCAN,
            library_id=library_id,
            log_file=str(log_path),
            description=description or f"Scan library {library_id}",
        )

        self._run_script(task, [_PYTHON, str(_PROJECT_ROOT / "main.py")], env_override)
        return task

    def launch_tmdb_update(
        self,
        library_id: int,
        description: str = "",
    ) -> TaskInfo:
        """Launch update_tmdb.py for a specific library."""
        task_id = self._make_id("tmdb")
        log_path = _LOG_DIR / f"{task_id}.log"

        env_override = {
            "LIBRARY_ID": str(library_id),
        }

        task = TaskInfo(
            id=task_id,
            task_type=TaskType.TMDB_UPDATE,
            library_id=library_id,
            log_file=str(log_path),
            description=description or f"TMDB update library {library_id}",
        )

        self._run_script(task, [_PYTHON, str(_PROJECT_ROOT / "update_tmdb.py")], env_override)
        return task

    def launch_migration(
        self,
        library_id: int,
        new_channel: str,
        new_channel_id: str | None = None,
        dry_run: bool = False,
        description: str = "",
    ) -> TaskInfo:
        """Launch migrate_channel_links.py for a specific library."""
        task_id = self._make_id("migrate")
        log_path = _LOG_DIR / f"{task_id}.log"

        cmd = [
            _PYTHON,
            str(_PROJECT_ROOT / "migrate_channel_links.py"),
            "--library-id", str(library_id),
            "--new-channel", new_channel,
        ]
        if new_channel_id:
            cmd.extend(["--new-channel-id", new_channel_id])
        if dry_run:
            cmd.append("--dry-run")

        task = TaskInfo(
            id=task_id,
            task_type=TaskType.MIGRATION,
            library_id=library_id,
            log_file=str(log_path),
            description=description or f"Migration library {library_id}{'(dry-run)' if dry_run else ''}",
            extra={"dry_run": dry_run, "new_channel": new_channel, "new_channel_id": new_channel_id},
        )

        self._run_script(task, cmd, {})
        return task

    def get_task(self, task_id: str) -> TaskInfo | None:
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[TaskInfo]:
        with self._lock:
            return list(reversed(self._tasks.values()))

    def get_task_logs(self, task_id: str, tail: int = 200) -> str:
        task = self.get_task(task_id)
        if not task:
            return ""
        log_path = Path(task.log_file)
        if not log_path.exists():
            return ""
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if tail and len(lines) > tail:
                lines = lines[-tail:]
            return "\n".join(lines)
        except Exception:
            return ""

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            proc = self._processes.get(task_id)
        if not task or not proc:
            return False
        if task.status != TaskStatus.RUNNING:
            return False
        try:
            proc.terminate()
            task.status = TaskStatus.CANCELLED
            task.finished_at = time.time()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _make_id(self, prefix: str) -> str:
        short = uuid.uuid4().hex[:8]
        return f"{prefix}-{short}"

    def _run_script(
        self,
        task: TaskInfo,
        cmd: list[str],
        env_override: dict[str, str],
    ) -> None:
        with self._lock:
            self._tasks[task.id] = task

        env = {**os.environ, **env_override}

        def _worker():
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            try:
                with open(task.log_file, "w", encoding="utf-8") as log_fh:
                    proc = subprocess.Popen(
                        cmd,
                        stdout=log_fh,
                        stderr=subprocess.STDOUT,
                        cwd=str(_PROJECT_ROOT),
                        env=env,
                        text=True,
                    )
                    with self._lock:
                        self._processes[task.id] = proc

                    proc.wait()

                task.exit_code = proc.returncode
                if task.status == TaskStatus.CANCELLED:
                    pass  # already set
                elif proc.returncode == 0:
                    task.status = TaskStatus.COMPLETED
                else:
                    task.status = TaskStatus.FAILED
            except Exception as exc:
                task.status = TaskStatus.FAILED
                # Write error to log
                try:
                    with open(task.log_file, "a", encoding="utf-8") as f:
                        f.write(f"\n\nFATAL ERROR: {exc}\n")
                except Exception:
                    pass
            finally:
                task.finished_at = time.time()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
