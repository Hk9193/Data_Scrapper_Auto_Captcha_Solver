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




# ─── Email Utilities ────────────────────────────────────────────────────────────

def normalize_obfuscated_text(text: str) -> str:
    """De-obfuscate common email patterns like 'user [at] domain [dot] com'."""
    if not text:
        return ""
    t = text.replace("%40", "@")
    t = re.sub(r"\s*\[at\]\s*|\s*\(at\)\s*|\s+at\s+", "@", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*\[dot\]\s*|\s*\(dot\)\s*", ".", t, flags=re.IGNORECASE)
    return t


def extract_emails(text: str) -> List[str]:
    """Extract and clean emails from raw text."""
    if not text:
        return []
    normalized = normalize_obfuscated_text(text)
    raw = EMAIL_PATTERN.findall(normalized)
    return [clean_email(e) for e in raw if clean_email(e)]


def clean_email(email: str) -> Optional[str]:
    """Return cleaned email or None if it should be discarded."""
    email = email.strip().lower()

    # Strip trailing snippet suffixes like .read, read, .more, more, or ellipsis
    email = re.sub(r"(\.(?:com|org|net|io|co|in|fr|de|uk|it|es|us|ae|me|ai|app|info|biz|eu|ca|gov|edu))(?:\.read|rea|\.more|more|\.contact|contact)+$", r"\1", email)
    email = re.sub(r"(\.[a-z]{2,4})\.read$", r"\1", email)
    email = re.sub(r"(\.[a-z]{2,4})read$", r"\1", email)
    email = email.rstrip(".")

    # Basic validity gate
    if len(email) > 254 or "." not in email.split("@")[-1]:
        return None

    # Blacklist check
    for kw in EMAIL_BLACKLIST_KEYWORDS:
        if kw in email:
            return None

    # Reject obvious junk suffixes left by bad regex matches
    for bad_ext in (".png", ".jpg", ".gif", ".jpeg", ".svg", ".webp", ".mp4", ".html", ".js", ".css"):
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
