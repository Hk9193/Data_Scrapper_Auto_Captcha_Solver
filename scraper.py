from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
    TimeoutError as PWTimeoutError,
)

from captcha_solver import auto_solve_captcha, captcha_cleared, ensure_captcha_checkbox
from config import (
    CAPTCHA_COOLDOWN_SECONDS,
    CAPTCHA_SOLVER,
    CONTINUOUS_MODE,
    CYCLE_RESTART_DELAY,
    DELAY_MAX,
    DELAY_MIN,
    HEADLESS,
    MAX_CAPTCHA_SOLVE_SECONDS,
    MAX_PAGES_PER_QUERY,
    MAX_RETRIES,
    MAX_TABS,
    PAGE_LOAD_TIMEOUT,
    PROXY_PASSWORD,
    PROXY_ROTATION_LIST,
    PROXY_SERVER,
    PROXY_USERNAME,
    QUERY_PROCESS_TIMEOUT_SECONDS,
    SEARCH_QUERIES,
    USER_AGENTS,
    VISIT_URLS,
)
from exporter import load_csv, save_to_csv, save_to_gsheet
from logger_setup import setup_logger
from playwright_stealth import Stealth
from recovery import (
    BrowserDeadError,
    is_closed_error,
    safe_close_context,
    safe_close_page,
)
from utils import (
    deduplicate_emails,
    extract_emails,
    extract_instagram_usernames,
    extract_links_from_text,
    is_expansion_link,
    normalize_text,
    random_delay,
    username_from_url,
)

logger = setup_logger("scraper")


@dataclass
class ScrapedRecord:
    username: str = ""
    email: str = ""
    source_url: str = ""
    query_used: str = ""
    found_in: str = ""
    page_title: str = ""

    def as_dict(self) -> Dict[str, str]:
        return {
            "username": self.username,
            "email": self.email,
            "source_url": self.source_url,
            "query_used": self.query_used,
            "found_in": self.found_in,
            "page_title": self.page_title,
        }


class GoogleScraper:
    def __init__(self, context: BrowserContext) -> None:
        self.context = context
        # Set True by search() when the last query was blocked by an
        # unsolvable CAPTCHA — lets the orchestrator relaunch the browser.
        self.captcha_blocked = False

    async def _new_page(self) -> Page:
        page = await self.context.new_page()
        await Stealth().apply_stealth_async(page)
        return page

    async def _handle_captcha(
        self,
        page: Page,
        timeout_seconds: Optional[float] = None,
    ) -> bool:
        """
        Handle Google CAPTCHA with retry logic AND a hard wall-clock budget.

        A single CAPTCHA session may never consume more than
        *timeout_seconds* (default MAX_CAPTCHA_SOLVE_SECONDS). Once the
        budget is exhausted we give up so that an unsolvable challenge can
        never silo the scraper for hours. Callers deal with `False` by
        taking a cooldown, relaunching the browser, and moving on.

        Returns True if CAPTCHA was cleared, False if it could not be
        resolved within the budget.
        Raises BrowserDeadError if the underlying browser is closed/dead.
        """
        MAX_CAPTCHA_ATTEMPTS = 5
        MANUAL_WAIT_TIMEOUT = 30  # seconds to wait for manual solve before retrying auto
        if timeout_seconds is None:
            timeout_seconds = MAX_CAPTCHA_SOLVE_SECONDS
        deadline = time.monotonic() + timeout_seconds

        for attempt in range(1, MAX_CAPTCHA_ATTEMPTS + 1):
            if time.monotonic() >= deadline:
                logger.error(
                    "CAPTCHA solve budget (%.0fs) exceeded after %d attempts. "
                    "Giving up on this CAPTCHA.",
                    timeout_seconds,
                    attempt - 1,
                )
                return False

            logger.info(
                "CAPTCHA handling attempt %d/%d...",
                attempt,
                MAX_CAPTCHA_ATTEMPTS,
            )

            # First, ensure the checkbox is actually checked (handles "expired" state)
            checkbox_checked = await ensure_captcha_checkbox(page)
            if captcha_cleared(page):
                logger.info("CAPTCHA cleared after checkbox interaction!")
                return True

            # Run automated solver, capped by the remaining wall-clock budget.
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            try:
                # Cap each auto-solve so a slow/hung solver is bounded.
                solved = await asyncio.wait_for(
                    auto_solve_captcha(page, method=CAPTCHA_SOLVER),
                    timeout=min(180.0, remaining),
                )
            except asyncio.TimeoutError:
                # The auto-solver didn't finish within budget — the browser is
                # probably fine (YOLO is CPU-bound). Give up on automated
                # solving for this session.
                logger.error(
                    "CAPTCHA auto-solve hit the %.0fs per-attempt budget.",
                    min(180.0, remaining),
                )
                solved = False
            except BrowserDeadError:
                raise

            if solved and captcha_cleared(page):
                logger.info("CAPTCHA solved successfully by automated solver!")
                return True

            # NOTE: We do NOT navigate to google.com just because "/sorry/index"
            # is in the URL. An expired CAPTCHA can remain on the same URL, and
            # navigating away does not help recover from the expired state.
            # The solver (auto_solve_captcha) now handles the EXPIRED state
            # internally by re-clicking the checkbox and waiting for a fresh
            # challenge. Navigation is only a last resort after the solver
            # has genuinely failed.
            if "/sorry/index" in page.url:
                logger.info(
                    "Still on Google CAPTCHA wall after solver attempt. "
                    "The solver may have detected an expired challenge. "
                    "Proceeding to manual fallback."
                )

            # If automated solver failed, wait for manual solve with timeout
            if attempt < MAX_CAPTCHA_ATTEMPTS:
                logger.warning(
                    "Automated solve attempt %d/%d failed. "
                    "Waiting up to %d seconds for manual solve in the open browser...",
                    attempt,
                    MAX_CAPTCHA_ATTEMPTS,
                    MANUAL_WAIT_TIMEOUT,
                )

                wait_elapsed = 0
                while wait_elapsed < MANUAL_WAIT_TIMEOUT:
                    if time.monotonic() >= deadline:
                        logger.error("CAPTCHA budget expired during manual wait.")
                        return False
                    if captcha_cleared(page):
                        logger.info("CAPTCHA solved manually! Resuming...")
                        return True
                    
                    # Check if the checkbox is still visible and clickable
                    # (handles the "Verification challenge expired" case)
                    try:
                        anchor_frame = None
                        for frame in page.frames:
                            if "recaptcha" in frame.url and "anchor" in frame.url:
                                anchor_frame = frame
                                break
                        if anchor_frame:
                            checkbox = await anchor_frame.query_selector("#recaptcha-anchor")
                            if checkbox:
                                is_checked = await checkbox.get_attribute("aria-checked")
                                if is_checked == "false":
                                    logger.info(
                                        "Checkbox unchecked (expired). Re-clicking..."
                                    )
                                    await checkbox.click()
                                    await asyncio.sleep(2)
                    except Exception as exc:
                        if is_closed_error(exc):
                            raise BrowserDeadError(str(exc)) from exc
                        pass

                    await asyncio.sleep(3)
                    wait_elapsed += 3

                logger.warning(
                    "Manual solve wait timed out (%d seconds). "
                    "Retrying automated solver...",
                    MANUAL_WAIT_TIMEOUT,
                )
            else:
                logger.error(
                    "All %d CAPTCHA handling attempts exhausted. "
                    "Giving up on this page.",
                    MAX_CAPTCHA_ATTEMPTS,
                )
                return False

        return False

    async def search(self, query: str) -> List[Dict[str, str]]:
        all_results: List[Dict[str, str]] = []
        self.captcha_blocked = False
        page = await self._new_page()

        try:
            try:
                await page.goto(
                    "https://www.google.com",
                    wait_until="domcontentloaded",
                    timeout=PAGE_LOAD_TIMEOUT,
                )
                search_box = await page.wait_for_selector(
                    "textarea[name='q'], input[name='q']", timeout=8000
                )
                if search_box:
                    await search_box.fill(query)
                    await asyncio.sleep(random.uniform(0.5, 1.2))
                    await search_box.press("Enter")
                    await page.wait_for_load_state("domcontentloaded")
            except Exception as exc:
                if is_closed_error(exc):
                    raise BrowserDeadError(str(exc)) from exc
                raise  # re-raise transient network errors for the outer handler

            for page_num in range(MAX_PAGES_PER_QUERY):
                # Handle CAPTCHA if present
                if "/sorry/index" in page.url or not captcha_cleared(page):
                    logger.critical("GOOGLE CAPTCHA DETECTED! Running solver...")
                    captcha_ok = await self._handle_captcha(page)
                    if not captcha_ok:
                        logger.error(
                            "Could not resolve CAPTCHA for query '%s' page %d. "
                            "Skipping remaining pages for this query.",
                            query,
                            page_num + 1,
                        )
                        self.captcha_blocked = True
                        break

                    # Wait for the page to finish navigating back to the search
                    # results after the CAPTCHA is cleared.
                    await asyncio.sleep(2.5)
                    try:
                        await page.wait_for_load_state(
                            "domcontentloaded", timeout=PAGE_LOAD_TIMEOUT
                        )
                    except Exception:
                        pass

                results = await self._extract_results(page, query)
                all_results.extend(results)

                next_btn = await page.query_selector("a#pnnext")
                if next_btn and page_num < MAX_PAGES_PER_QUERY - 1:
                    await random_delay(DELAY_MIN, DELAY_MAX)
                    await next_btn.click()
                    await page.wait_for_load_state("domcontentloaded")
                else:
                    break

        except BrowserDeadError:
            raise
        except Exception as exc:
            logger.error("Search error on query '%s': %s", query, exc)
        finally:
            await safe_close_page(page)

        return all_results

    async def _extract_results(self, page: Page, query: str) -> List[Dict[str, str]]:
        results = []
        blocks = await page.query_selector_all("div.g, div.tF2Cxc")
        for block in blocks:
            try:
                title_el = await block.query_selector("h3")
                link_el = await block.query_selector("a")
                snippet_el = await block.query_selector("div.VwiC3b, span.st")

                title = await title_el.inner_text() if title_el else ""
                href = await link_el.get_attribute("href") if link_el else ""
                snippet = await snippet_el.inner_text() if snippet_el else ""

                if href and href.startswith("http"):
                    results.append({
                        "title": normalize_text(title),
                        "url": href.split("&")[0],
                        "snippet": normalize_text(snippet),
                        "query": query,
                    })
            except Exception:
                continue
        return results


class DataScraper:
    def __init__(self) -> None:
        self.global_seen_emails: Set[str] = set()
        self.global_seen_usernames: Set[str] = set()
        self.records: List[ScrapedRecord] = []
        self._load_existing_data()

    def _load_existing_data(self) -> None:
        rows = load_csv()
        for row in rows:
            if row.get("email"):
                self.global_seen_emails.add(row["email"].lower())
            if row.get("username"):
                self.global_seen_usernames.add(row["username"].lower())

    def _process_target(self, target: Dict[str, str]) -> None:
        """Extract emails/usernames from a single Google result (snippet + title)."""
        title = target.get("title", "")
        snippet = target.get("snippet", "")
        url = target.get("url", "")
        query = target.get("query", "")

        # Combine all available text and extract emails
        combined_text = f"{title}\n{snippet}\n{url}"
        emails = extract_emails(combined_text)
        usernames = extract_instagram_usernames(combined_text)

        # Deduplicate against global seen sets
        new_emails = deduplicate_emails(emails, self.global_seen_emails)
        new_usernames = [
            u for u in usernames
            if u and u not in self.global_seen_usernames
        ]
        for u in new_usernames:
            self.global_seen_usernames.add(u)

        # Create a record per email (primary output)
        if new_emails:
            for email in new_emails:
                username = new_usernames[0] if new_usernames else ""
                self.records.append(ScrapedRecord(
                    username=username,
                    email=email,
                    source_url=url,
                    query_used=query,
                    found_in="google_snippet",
                    page_title=title,
                ))
            logger.info("Found %d new email(s) from %s", len(new_emails), url)
        elif new_usernames:
            # Record Instagram username even if no email found
            for username in new_usernames:
                self.records.append(ScrapedRecord(
                    username=username,
                    email="",
                    source_url=url,
                    query_used=query,
                    found_in="google_snippet",
                    page_title=title,
                ))

    async def _visit_and_extract(self, context: BrowserContext, target: Dict[str, str]) -> None:
        """Visit a URL and extract emails/usernames from the page content."""
        url = target.get("url", "")
        if not url:
            return
        page = await self._new_page(context)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            content = await page.content()
            title = await page.title()
            emails = extract_emails(content)
            usernames = extract_instagram_usernames(content)

            new_emails = deduplicate_emails(emails, self.global_seen_emails)
            new_usernames = [
                u for u in usernames
                if u and u not in self.global_seen_usernames
            ]
            for u in new_usernames:
                self.global_seen_usernames.add(u)

            for email in new_emails:
                username = new_usernames[0] if new_usernames else ""
                self.records.append(ScrapedRecord(
                    username=username,
                    email=email,
                    source_url=url,
                    query_used=target.get("query", ""),
                    found_in="page_content",
                    page_title=title,
                ))
            if new_emails:
                logger.info("Visited %s → found %d new email(s)", url, len(new_emails))
        except Exception as exc:
            logger.warning("Failed to visit %s: %s", url, exc)
        finally:
            await safe_close_page(page)

    async def _new_page(self, context: BrowserContext) -> Page:
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        return page

    async def run(self) -> None:
        """Run the scraper continuously (24/7) until manually stopped.

        Every possible failure mode is converted into a controlled recovery:
          - a hung Playwright call  -> per-query asyncio.wait_for timeout
          - a dead browser/context -> BrowserDeadError -> recreate context
          - an unsolvable CAPTCHA  -> time-budgeted -> cooldown -> fresh
            browser session, then continue with the next query
        """
        logger.info("=" * 60)
        logger.info("DJ Email Scraper — starting (continuous 24/7 mode)")
        logger.info("Queries : %d  |  Max pages: %d  |  Max tabs: %d",
                    len(SEARCH_QUERIES), MAX_PAGES_PER_QUERY, MAX_TABS)
        if CONTINUOUS_MODE:
            logger.info("Continuous mode enabled — will keep running until manually stopped.")
        logger.info("=" * 60)

        while True:
            try:
                await self._run_cycle()
            except KeyboardInterrupt:
                logger.info("Received stop signal (Ctrl+C). Shutting down cleanly...")
                break
            except Exception as exc:
                logger.exception("Fatal error in run cycle: %s", exc)
            finally:
                self._flush_records()

            if not CONTINUOUS_MODE:
                logger.info("Single pass complete. Total unique emails: %d",
                            len(self.global_seen_emails))
                break

            logger.info("Cycle finished. Restarting in %.1fs...", CYCLE_RESTART_DELAY)
            try:
                await asyncio.sleep(CYCLE_RESTART_DELAY)
            except asyncio.CancelledError:
                break
            except KeyboardInterrupt:
                logger.info("Stop requested during restart delay.")
                break

        self._flush_records()
        logger.info("Scraper stopped. Total unique emails collected: %d",
                    len(self.global_seen_emails))

    # ── Cycle orchestrator ──────────────────────────────────────────────────

    async def _run_cycle(self) -> None:
        """One full pass over SEARCH_QUERIES with a fresh browser context."""
        async with async_playwright() as pw:
            context: Optional[BrowserContext] = None
            google_scraper: Optional[GoogleScraper] = None
            try:
                context = await self._launch_context(pw)
                google_scraper = GoogleScraper(context)
                logger.info("Browser context ready. Processing queries...")

                for query in SEARCH_QUERIES:
                    if context is None:
                        logger.warning("Context was lost; relaunching browser.")
                        context = await self._launch_context(pw)
                        google_scraper = GoogleScraper(context)

                    try:
                        await asyncio.wait_for(
                            self._process_one_query(google_scraper, context, query),
                            timeout=QUERY_PROCESS_TIMEOUT_SECONDS,
                        )
                    except asyncio.TimeoutError:
                        # A Playwright call hung (browser half-dead). Force a
                        # clean browser recreation and move on — never freeze.
                        logger.error(
                            "Query '%s' exceeded the %ds processing ceiling. "
                            "Recreating browser and continuing.",
                            query,
                            QUERY_PROCESS_TIMEOUT_SECONDS,
                        )
                        self._flush_records()
                        await safe_close_context(context)
                        context = await self._launch_context(pw)
                        google_scraper = GoogleScraper(context)
                    except BrowserDeadError as exc:
                        logger.error(
                            "Browser died while processing query '%s': %s. "
                            "Recreating browser and continuing.",
                            query,
                            exc,
                        )
                        self._flush_records()
                        await safe_close_context(context)
                        context = await self._launch_context(pw)
                        google_scraper = GoogleScraper(context)
                    except Exception as exc:
                        logger.exception(
                            "Unexpected error while processing query '%s': %s",
                            query,
                            exc,
                        )
                        self._flush_records()
            finally:
                await safe_close_context(context)

    async def _launch_context(self, pw: Playwright) -> BrowserContext:
        """Launch a persistent browser context, retrying on profile-lock and
        falling back to a fresh profile directory if the main one is stuck."""
        base_dir = os.path.join(os.getcwd(), "browser_profile")
        launch_kwargs = dict(
            user_data_dir=base_dir,
            headless=HEADLESS,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        last_err: Optional[Exception] = None
        for attempt in range(1, 4):
            try:
                context = await pw.chromium.launch_persistent_context(**launch_kwargs)
                logger.info("Launched persistent browser context (attempt %d).", attempt)
                return context
            except Exception as exc:  # e.g. profile lock still held by zombie chrome
                last_err = exc
                logger.warning(
                    "Browser launch failed (attempt %d/3): %s", attempt, exc
                )
                # Give the OS time to release the profile/database locks.
                await asyncio.sleep(5 * attempt)

        # Last resort: use a fresh profile directory so a stale lock or a
        # corrupted profile can never stop the scraper permanently.
        alt_dir = os.path.join(os.getcwd(), f"browser_profile_{int(time.time())}")
        logger.error(
            "Could not reuse '%s' after retries (%s). Using fresh profile '%s'.",
            base_dir,
            last_err,
            alt_dir,
        )
        launch_kwargs["user_data_dir"] = alt_dir
        return await pw.chromium.launch_persistent_context(**launch_kwargs)

    async def _process_one_query(
        self,
        google_scraper: GoogleScraper,
        context: BrowserContext,
        query: str,
    ) -> None:
        """Search one query, extract emails, optionally visit URLs, save."""
        google_scraper.captcha_blocked = False
        results = await google_scraper.search(query)
        logger.info("Query '%s' returned %d results.", query, len(results))

        if google_scraper.captcha_blocked:
            logger.warning(
                "Query '%s' was blocked by an unsolvable CAPTCHA. "
                "Taking a %.0fs cooldown, then relaunching the browser for a "
                "fresh session before continuing with the next query.",
                query,
                CAPTCHA_COOLDOWN_SECONDS,
            )
            self._flush_records()
            await asyncio.sleep(CAPTCHA_COOLDOWN_SECONDS)
            # Signal the orchestrator to recreate the browser context.
            raise BrowserDeadError(
                f"CAPTCHA-blocked query: '{query[:60]}' — forcing browser recreation"
            )

        # Extract emails from snippets (always)
        for target in results:
            self._process_target(target)

        # Optionally visit URLs for deeper extraction
        if VISIT_URLS:
            for target in results:
                try:
                    await self._visit_and_extract(context, target)
                except Exception as exc:
                    logger.warning("Visit task failed for %s: %s",
                                   target.get("url", "?"), exc)

        # Save incrementally after each query to avoid data loss
        self._flush_records(query=query)

    def _flush_records(self, query: str = "") -> None:
        """Persist any pending records to CSV/Sheets and clear the buffer."""
        if not self.records:
            return
        dicts = [r.as_dict() for r in self.records]
        try:
            save_to_csv(dicts)
            save_to_gsheet(dicts)
            logger.info("Saved %d record(s)%s.",
                        len(dicts),
                        f" after query '{query}'" if query else "")
        except Exception as exc:
            logger.error("Failed to save %d record(s): %s", len(dicts), exc)
        finally:
            self.records.clear()



if __name__ == "__main__":
    scraper = DataScraper()
    try:
        asyncio.run(scraper.run())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — final cleanup.")
    except Exception as exc:
        logger.exception("Unhandled top-level error: %s", exc)