"""Uvicorn entry point for the Telegram Movie Library API.

Usage:
    python -m backend.run
    python backend/run.py
"""
from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
