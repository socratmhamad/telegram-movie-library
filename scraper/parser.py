from __future__ import annotations

from dataclasses import dataclass
import re


YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")
QUALITY_PATTERN = re.compile(r"\b(144p|240p|360p|480p|720p|1080p|2160p)\b", re.IGNORECASE)
NOISE_PATTERNS = (
    re.compile(r"\b(?:4k|hdrip|webrip|web-dl|bluray|blu-ray|brrip|dvdrip|mp4|mkv|avi)\b", re.IGNORECASE),
    re.compile(r"\b(?:x264|x265|h\.?264|h\.?265|hevc|aac|dual audio|multi audio)\b", re.IGNORECASE),
    re.compile(r"\b(?:download|watch|movie|movies|full movie|new link)\b", re.IGNORECASE),
    re.compile(r"\[?cinemamlt\]?", re.IGNORECASE),
    re.compile(r"https?://\S+", re.IGNORECASE),
    re.compile(r"@\w+"),
    re.compile(r"#[\w-]+"),
)


@dataclass(frozen=True)
class ParsedMovie:
    title: str
    quality: str | None


def extract_movie_title(message_text: str | None) -> str | None:
    parsed_movie = parse_movie_message(message_text)
    if not parsed_movie:
        return None

    return parsed_movie.title


def parse_movie_message(message_text: str | None) -> ParsedMovie | None:
    """
    Extract a likely movie title and supported video quality from a Telegram message.

    This intentionally stays conservative. It accepts common channel formats like:
    - Movie Title (2024)
    - Movie Title 2024 1080p
    - Movie Title
    """
    if not message_text:
        return None

    candidates = [
        line.strip()
        for line in message_text.splitlines()
        if line.strip() and not re.search(r'\b(?:imdb|rating|تقييم|التقييم|التقيم)\b', line, re.IGNORECASE)
    ]

    for candidate in candidates:
        quality = _extract_quality(candidate)
        title = _clean_title(candidate)
        if _is_valid_title(title):
            return ParsedMovie(title=title, quality=quality)

    return None


def _extract_quality(text: str) -> str | None:
    match = QUALITY_PATTERN.search(text)
    if not match:
        return None

    return match.group(1).lower()


def _clean_title(text: str) -> str:
    text = text.replace("_", " ")
    
    # Remove Arabic characters
    text = re.sub(r"[\u0600-\u06FF]+", " ", text)
    
    # Remove emojis and non-standard symbols (keep words, spaces, and basic punctuation)
    text = re.sub(r"[^\w\s\.,!\?:\-\'\"\(\)\[\]&]", " ", text)
    
    text = re.sub(r"[\[\]{}]", " ", text)
    text = QUALITY_PATTERN.sub(" ", text)

    for pattern in NOISE_PATTERNS:
        text = pattern.sub(" ", text)

    text = re.sub(r"[-|:]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,-:;|")


def _is_valid_title(title: str) -> bool:
    if len(title) < 2:
        return False

    if len(title.split()) > 12:
        return False

    if not re.search(r"[A-Za-z0-9]", title):
        return False

    return True
