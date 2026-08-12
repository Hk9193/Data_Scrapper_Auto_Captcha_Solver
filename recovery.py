"""
recovery.py — Robustness helpers for 24/7 operation.

Provides:
  - BrowserDeadError    : raised when the Playwright browser/context/page is
                          closed or unreachable, so the caller can safely
                          recreate the browser instead of spinning forever
                          on a dead object.
  - is_closed_error()   : recognises the classic Playwright "Target page,
                          context or browser has been closed" exceptions.
  - safe_close_page()   : close a page without raising when already closed.
  - safe_close_context(): close a context without raising when already closed.
  - context_alive()     : cheap liveness check for a browser context.
"""

from __future__ import annotations

import logging

from playwright.async_api import BrowserContext, Page

logger = logging.getLogger("scraper.recovery")


class BrowserDeadError(Exception):
    """Raised when the browser / context / page is closed or unreachable."""


class CAPTCHABlockError(Exception):
    """Raised when a query pass is interrupted by an unsolvable CAPTCHA.

    The caller should mark the query PENDING, recreate the browser, and retry
    the SAME query from the saved page — never skip it.
    """


class QueryIncompleteError(Exception):
    """Raised when a query pass ends without completing (e.g. transient
    network failure). The caller should retry the SAME query from the last
    completed page."""


class GoogleAutomatedQueryBlockError(Exception):
    """Raised when Google serves its hard rate-limit wall — "Try again
    later / Your computer or network may be sending automated queries."

    This is NOT a solvable CAPTCHA (no checkbox / image / audio challenge),
    so the CAPTCHA solver and the cadence used at the /sorry/index wall must
    NOT apply. The caller should:
      - keep the current query + page + collected results PENDING,
      - stop all Google traffic immediately (no tight browser recreation),
      - apply a bounded exponential backoff/cooldown,
      - periodically probe whether Google is usable again,
      - resume the EXACT pending query/page once Google is available,
      - if the block persists, pause/exit the Google worker rather than
        burning retries."""


# Classic Playwright closed-target messages (all flavours).
_CLOSED_MARKERS = (
    "Target page, context or browser has been closed",
    "has been closed",
    "Target closed",
    "browser has been closed",
    "Connection closed",
    "Browser process failed to launch",
    "Browser closed",
    "Protocol error",
    "Cannot read properties of undefined",
)


def is_closed_error(exc: BaseException) -> bool:
    """Return True if *exc* stems from a closed/dead browser target."""
    text = f"{type(exc).__name__}: {exc}"
    return any(marker.lower() in text.lower() for marker in _CLOSED_MARKERS)


def context_alive(context: BrowserContext) -> bool:
    """
    Cheap, non-awaitable liveness check.

    If Playwright itself raises here, or the browser handle is gone, or no
    page can be reached, we treat the context as dead. This is deliberately
    lenient — hard timeout enforcement still lives in asyncio.wait_for.
    """
    try:
        if context is None:
            return False
        # Accessing .browser()/.pages can raise if the connection is dead.
        browser = context.browser
        if browser is None:
            return False
        # Touch a property that forces a protocol round-trip is NOT done here
        # (it could hang on a dead browser). Cheap local checks only.
        return True
    except Exception:
        return False


async def safe_close_page(page: Page) -> None:
    """Close *page* ignoring errors (never raises, never hangs indefinitely)."""
    if page is None:
        return
    try:
        await page.close()
    except Exception as exc:
        logger.debug("Ignored error while closing page: %s", exc)


async def safe_close_context(context: BrowserContext) -> None:
    """Close *context* and its browser ignoring errors."""
    if context is None:
        return
    try:
        browser = context.browser
        if browser is not None:
            await browser.close()
    except Exception as exc:
        logger.debug("Ignored error while closing browser: %s", exc)
    try:
        await context.close()
    except Exception as exc:
        logger.debug("Ignored error while closing context: %s", exc)
    finally:
        # Give the OS a moment to release the profile lock.
        import asyncio

        await asyncio.sleep(1.0)