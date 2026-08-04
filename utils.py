"""
utils.py — Shared helpers: regex, cleaning, deduplication, delays
"""

import re
import asyncio
import random
import logging
from typing import Set, List, Optional

from config import (
    EMAIL_BLACKLIST_KEYWORDS,
    DELAY_MIN,
    DELAY_MAX,
    EXPANSION_DOMAINS,
)

logger = logging.getLogger("scraper.utils")

# ─── Regex Patterns ────────────────────────────────────────────────────────────

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

INSTAGRAM_PATTERN = re.compile(
    r"instagram\.com/([A-Za-z0-9._]{1,30})/?",
    re.IGNORECASE,
)

INSTAGRAM_RESERVED = {
    "p", "tv", "reel", "reels", "stories", "explore",
    "accounts", "about", "press", "api", "blog",
    "jobs", "help", "legal", "privacy", "security",
    "directory", "hashtag", "shoppingbag", "web",
    "graphql", "static",
}


# ─── Email Utilities ────────────────────────────────────────────────────────────

def extract_emails(text: str) -> List[str]:
    """Extract and clean emails from raw text."""
    if not text:
        return []
    raw = EMAIL_PATTERN.findall(text)
    return [clean_email(e) for e in raw if clean_email(e)]


def clean_email(email: str) -> Optional[str]:
    """Return cleaned email or None if it should be discarded."""
    email = email.strip().lower()

    # Basic validity gate
    if len(email) > 254 or "." not in email.split("@")[-1]:
        return None

    # Blacklist check
    for kw in EMAIL_BLACKLIST_KEYWORDS:
        if kw in email:
            return None

    # Reject obvious junk suffixes left by bad regex matches
    for bad_ext in (".png", ".jpg", ".gif", ".jpeg", ".svg", ".webp", ".mp4"):
        if email.endswith(bad_ext):
            return None

    return email


def deduplicate_emails(
    emails: List[str],
    global_seen: Set[str],
) -> List[str]:
    """Return only emails not already in *global_seen*, then add them."""
    new_emails: List[str] = []
    for e in emails:
        if e and e not in global_seen:
            global_seen.add(e)
            new_emails.append(e)
    return new_emails


# ─── Instagram Username Utilities ──────────────────────────────────────────────

def extract_instagram_usernames(text: str) -> List[str]:
    """Extract Instagram usernames from URLs inside arbitrary text."""
    matches = INSTAGRAM_PATTERN.findall(text)
    results: List[str] = []
    for m in matches:
        username = m.strip("/").split("?")[0]
        if username and username.lower() not in INSTAGRAM_RESERVED:
            results.append(username.lower())
    return list(dict.fromkeys(results))  # preserve order, deduplicate


def username_from_url(url: str) -> Optional[str]:
    """Return Instagram username from a URL string, or None."""
    usernames = extract_instagram_usernames(url)
    return usernames[0] if usernames else None


# ─── Link Expansion Utilities ──────────────────────────────────────────────────

def is_expansion_link(url: str) -> bool:
    """Return True if URL points to a known bio-aggregator / linktree."""
    url_lower = url.lower()
    return any(domain in url_lower for domain in EXPANSION_DOMAINS)


def extract_links_from_text(text: str) -> List[str]:
    """Extract all HTTP/HTTPS links from raw text."""
    link_pattern = re.compile(
        r"https?://[^\s\"'<>]+",
        re.IGNORECASE,
    )
    return link_pattern.findall(text)


# ─── Delay Helpers ─────────────────────────────────────────────────────────────

async def random_delay(
    low: float = DELAY_MIN,
    high: float = DELAY_MAX,
) -> None:
    """Async sleep for a random duration between *low* and *high* seconds."""
    delay = random.uniform(low, high)
    logger.debug("Sleeping %.2fs", delay)
    await asyncio.sleep(delay)


def sync_random_delay(
    low: float = DELAY_MIN,
    high: float = DELAY_MAX,
) -> None:
    """Synchronous version (use in non-async contexts)."""
    import time
    time.sleep(random.uniform(low, high))


# ─── Text Normalisation ────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces."""
    return re.sub(r"\s+", " ", text or "").strip()
