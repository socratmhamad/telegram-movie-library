from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List


TELEGRAM_LINK_PATTERN = re.compile(
    r"https?://t\.me/[^\s\"'<>]+",
    re.IGNORECASE,
)

NOISE_PATTERNS = (
    re.compile(r"\b(?:download|watch|series|season|episode|new link)\b", re.IGNORECASE),
    re.compile(r"https?://\S+", re.IGNORECASE),
    re.compile(r"@\w+"),
    re.compile(r"#[\w-]+"),
)


@dataclass(frozen=True)
class ParsedSeries:
    title: str
    telegram_link: str | None


def parse_series_message(message_text: str | None) -> ParsedSeries | None:
    """
    Extract a TV series title and Telegram channel link from a message.

    Expected message format:
    - Title on the first meaningful line
    - A t.me link somewhere in the message body
    """
    if not message_text:
        return None

    # Extract all Telegram links from the full message
    links = TELEGRAM_LINK_PATTERN.findall(message_text)
    telegram_link = links[0] if links else None

    # Find the title from the first non-empty line
    candidates = [
        line.strip()
        for line in message_text.splitlines()
        if line.strip()
    ]

    for candidate in candidates:
        title = _clean_title(candidate)
        if _is_valid_title(title):
            return ParsedSeries(title=title, telegram_link=telegram_link)

    return None


def _clean_title(text: str) -> str:
    text = text.replace("_", " ")

    # Remove Arabic characters
    text = re.sub(r"[\u0600-\u06FF]+", " ", text)

    # Remove emojis and non-standard symbols (keep words, spaces, and basic punctuation)
    text = re.sub(r"[^\w\s\.,!\?:\-\'\"()\[\]&]", " ", text)

    text = re.sub(r"[\[\]{}]", " ", text)

    for pattern in NOISE_PATTERNS:
        text = pattern.sub(" ", text)

    text = re.sub(r"[-|:]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,-:;|")


def _is_valid_title(title: str) -> bool:
    if len(title) < 2:
        return False

    if len(title.split()) > 15:
        return False

    if not re.search(r"[A-Za-z0-9]", title):
        return False

    # Skip lines that look like just a URL
    if title.startswith("http"):
        return False

    return True


# ---------------------------------------------------------------------------
# Bulk-message parser: handles messages with many series in one message
# Format: "1028- Title (Year) 👇\nhttps://t.me/...\n\n1029- Title ..."
# ---------------------------------------------------------------------------

# Matches a numbered entry header like "1028- Shining Vale (2022) 👇"
_BULK_ENTRY_HEADER = re.compile(
    r"^\d+\s*[-–—.)\]]\s*(.+)",
    re.MULTILINE,
)


def parse_bulk_series_message(message_text: str | None) -> List[ParsedSeries] | None:
    """Parse a message containing multiple series entries.

    Returns a list of ParsedSeries if the message matches the bulk format
    (3+ numbered entries detected), otherwise returns None so the caller
    can fall back to the single-entry parser.
    """
    if not message_text:
        return None

    # Quick check: need at least 3 numbered-entry headers to treat as bulk
    headers = _BULK_ENTRY_HEADER.findall(message_text)
    if len(headers) < 3:
        return None

    # Split the message into blocks around numbered headers.
    # Each block: the header line + everything until the next header.
    blocks = re.split(r"(?=^\d+\s*[-–—.)\]]\s*)", message_text, flags=re.MULTILINE)

    results: List[ParsedSeries] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Must start with a numbered header
        header_match = re.match(r"^\d+\s*[-–—.)\]]\s*(.+)", block)
        if not header_match:
            continue

        # Extract t.me link from this block
        links = TELEGRAM_LINK_PATTERN.findall(block)
        telegram_link = links[0] if links else None

        # Title is the first line after stripping the number prefix
        raw_title = header_match.group(1).strip()
        title = _clean_title(raw_title)

        if _is_valid_title(title):
            results.append(ParsedSeries(title=title, telegram_link=telegram_link))

    return results if results else None

