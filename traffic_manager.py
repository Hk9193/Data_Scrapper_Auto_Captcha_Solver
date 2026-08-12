"""
traffic_manager.py — Global Google request rate limiting, backoff, and
persisted query progress for reliable 24/7 operation.

This module does NOT try to bypass or disguise Google's anti-bot systems. It
purely *reduces* the amount of Google traffic we generate and makes recovery
gentle and deterministic:

  - TrafficManager.throttle_google_request(): global min-interval + sliding
    window rate limit applied to EVERY Google navigation (homepage, search,
    pagination). It also acts as a process-wide lock so concurrent tabs/tasks
    can never fire simultaneous Google requests.
  - TrafficManager.backoff_delay(): jittered exponential backoff used before
    retrying a blocked/failed Google request. A blocked request is NEVER
    retried immediately.
  - ProgressStore: persists the exact query -> last-extracted-page + completion
    timestamp to a JSON file, so the scraper can pause/resume and skip
    re-crawling queries that were already fully completed recently (the #1
    source of duplicate Google traffic).

All timing values are overridable from config.py.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import time
from typing import Dict, Optional

from config import (
    BACKOFF_BASE_SECONDS,
    BACKOFF_MAX_SECONDS,
    CAPTCHA_BACKOFF_BASE_SECONDS,
    CAPTCHA_BACKOFF_MAX_SECONDS,
    MAX_REQUESTS_PER_WINDOW,
    QUERY_CACHE_INTERVAL_SECONDS,
    REQUEST_MIN_INTERVAL_SECONDS,
    REQUEST_WINDOW_SECONDS,
    STATE_FILE,
)

logger = logging.getLogger("scraper.traffic")

class TrafficManager:
    """Process-wide Google request rate limiter + backoff helper.

    Thread-safety / concurrency: all pacing state is guarded by an asyncio
    lock and the throttle itself serialises Google requests, so no amount of
    tabs/tasks can generate overlapping or bursty Google traffic.
    """

    def __init__(
        self,
        min_interval: float = REQUEST_MIN_INTERVAL_SECONDS,
        window_seconds: float = REQUEST_WINDOW_SECONDS,
        max_requests_per_window: int = MAX_REQUESTS_PER_WINDOW,
    ) -> None:
        self._lock = asyncio.Lock()
        self.min_interval = float(min_interval)
        self.window_seconds = float(window_seconds)
        self.max_per_window = int(max_requests_per_window)
        self._timestamps: list = []          # recent request start times
        self._total_requests = 0
        self._blocked_count = 0
        self._backoff_seconds_total = 0.0
        self._last_request_at = 0.0

    # ── Rate limiting ──────────────────────────────────────────────────────────

    async def throttle_google_request(self, label: str = "request") -> None:
        """Wait until we are allowed to fire one Google request, then record it.

        Enforces, in order:
          1. a minimum gap between consecutive Google requests,
          2. a maximum number of requests inside a sliding window,
          3. a process-wide lock so concurrent calls never overlap.
        """
        async with self._lock:
            now = time.monotonic()

            # Minimum gap between consecutive Google requests.
            if self._timestamps:
                gap = now - self._timestamps[-1]
                if gap < self.min_interval:
                    wait = self.min_interval - gap
                    # A little jitter so consecutive sleeps don't align.
                    await asyncio.sleep(wait * random.uniform(0.8, 1.2))
                    now = time.monotonic()

            # Sliding-window cap on total requests.
            self._timestamps = [t for t in self._timestamps
                                if now - t < self.window_seconds]
            while self._timestamps and len(self._timestamps) >= self.max_per_window:
                oldest = self._timestamps[0]
                sleep_for = self.window_seconds - (now - oldest)
                if sleep_for <= 0:
                    break
                await asyncio.sleep(sleep_for)
                now = time.monotonic()
                self._timestamps = [t for t in self._timestamps
                                    if now - t < self.window_seconds]

            self._timestamps.append(now)
            self._total_requests += 1
            self._last_request_at = now
            logger.debug(
                "Google request %d ('%s') allowed (rate window: %d active).",
                self._total_requests, label, len(self._timestamps),
            )
# ── Backoff ────────────────────────────────────────────────────────────────

    def backoff_delay(
        self,
        attempt: int,
        *,
        kind: str = "generic",
    ) -> float:
        """Seconds to sleep before the next attempt.

        Exponential growth (2x per attempt) with full jitter so retries from
        many clients/cycles never synchronise. `kind` picks base/max:
          - "captcha": after Google served a CAPTCHA/unsusual-traffic wall,
          - "generic":  transient errors, browser deaths, timeouts.
        """
        if kind == "captcha":
            base, cap = CAPTCHA_BACKOFF_BASE_SECONDS, CAPTCHA_BACKOFF_MAX_SECONDS
        else:
            base, cap = BACKOFF_BASE_SECONDS, BACKOFF_MAX_SECONDS
        exponent = max(0, int(attempt) - 1)
        delay = min(base * (2 ** exponent), cap)
        delay *= random.uniform(0.5, 1.5)  # full jitter
        return round(delay, 2)

    async def sleep_backoff(self, attempt: int, *, kind: str = "generic",
                            label: str = "") -> None:
        """Sleep `backoff_delay(...)` and record diagnostics."""
        delay = self.backoff_delay(attempt, kind=kind)
        self._backoff_seconds_total += delay
        self._blocked_count += 1
        logger.warning(
            "Traffic backoff (%s, attempt %d) sleeping %.1fs%s",
            kind, attempt, delay, f" after {label}" if label else "",
        )
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            logger.warning("Traffic backoff cancelled (%s attempt %d).",
                           kind, attempt)
            raise

    # ── Diagnostics ────────────────────────────────────────────────────────────

    def report(self) -> Dict[str, float]:
        """Snapshot of traffic diagnostics for logging."""
        now = time.monotonic()
        rate = len([t for t in self._timestamps
                    if now - t < self.window_seconds]) / (self.window_seconds / 60.0)
        return {
            "total_google_requests": self._total_requests,
            "window_active_requests": len(
                [t for t in self._timestamps if now - t < self.window_seconds]
            ),
            "current_rate_per_minute": round(rate, 2),
            "blocked_events": self._blocked_count,
            "backoff_seconds_total": round(self._backoff_seconds_total, 1),
        }

class ProgressStore:
    """Persisted per-query scrape progress (pause/resume + query cache).

    A query is considered *fully completed* when its recorded page equals
    max_pages. Such queries are skipped for re-crawl for `cache_interval`
    seconds, which eliminates the duplicate Google requests that otherwise
    happen on every continuous-mode cycle.
    """

    def __init__(
        self,
        path: str = STATE_FILE,
        cache_interval: float = QUERY_CACHE_INTERVAL_SECONDS,
        max_pages: int = 15,
    ) -> None:
        self.path = path
        self.cache_interval = float(cache_interval)
        self.max_pages = int(max_pages)
        self._data: Dict[str, Dict] = {}
        self.load()

    def load(self) -> None:
        try:
            if os.path.isfile(self.path):
                with open(self.path, "r", encoding="utf-8") as fh:
                    self._data = json.load(fh)
        except Exception as exc:
            logger.warning("Could not load state file %s: %s", self.path, exc)
            self._data = {}

    def save(self) -> None:
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, sort_keys=True)
            os.replace(tmp, self.path)
        except Exception as exc:
            logger.warning("Could not persist state file %s: %s", self.path, exc)

    def record_page(self, query: str, page: int) -> None:
        """Record the highest *completed* page for a query (0-based).

        This allows a crashed run to resume from the last completed page.
        """
        entry = self._data.get(query) or {"page": 0, "completed_at": 0.0}
        entry["page"] = max(int(entry.get("page", 0) or 0), int(page))
        self._data[query] = entry
        self.save()

    def mark_query_complete(self, query: str) -> None:
        """Mark a query fully crawled so it is skipped for `cache_interval`."""
        entry = self._data.get(query) or {"page": 0, "completed_at": 0.0}
        entry["page"] = self.max_pages
        entry["completed_at"] = time.time()
        self._data[query] = entry
        self.save()

    def resume_page(self, query: str) -> int:
        """Last completed page for a query (0-based), for crash resume."""
        entry = self._data.get(query) or {}
        page = int(entry.get("page", 0) or 0)
        if page >= self.max_pages:
            return 0  # fully completed; only start over after cache expiry
        return page

    def should_skip(self, query: str, now: Optional[float] = None) -> bool:
        """True if the query fully completed recently -> skip re-crawl."""
        entry = self._data.get(query) or {}
        if int(entry.get("page", 0) or 0) < self.max_pages:
            return False
        completed_at = float(entry.get("completed_at", 0.0) or 0.0)
        if completed_at <= 0:
            return False
        now = time.time() if now is None else now
        return (now - completed_at) < self.cache_interval

    @property
    def cached_count(self) -> int:
        return sum(1 for q in self._data if self.should_skip(q))


# Module-level singletons shared by every cycle / tab.
traffic = TrafficManager()
store = ProgressStore()