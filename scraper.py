from __future__ import annotations

import asyncio
import logging
import os
import random
import re
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
    CAPTCHA_SOLVER,
    DELAY_MAX,
    DELAY_MIN,
    HEADLESS,
    MAX_PAGES_PER_QUERY,
    MAX_RETRIES,
    MAX_TABS,
    PAGE_LOAD_TIMEOUT,
    PROXY_PASSWORD,
    PROXY_ROTATION_LIST,
    PROXY_SERVER,
    PROXY_USERNAME,
    SEARCH_QUERIES,
    USER_AGENTS,
    VISIT_URLS,
)
from exporter import load_csv, save_to_csv, save_to_gsheet
from logger_setup import setup_logger
from playwright_stealth import Stealth
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

    async def _new_page(self) -> Page:
        page = await self.context.new_page()
        await Stealth().apply_stealth_async(page)
        return page

    async def _handle_captcha(self, page: Page) -> bool:
        """
        Handle Google CAPTCHA with retry logic.
        Returns True if CAPTCHA was cleared, False if it could not be resolved.
        """
        MAX_CAPTCHA_ATTEMPTS = 5
        MANUAL_WAIT_TIMEOUT = 30  # seconds to wait for manual solve before retrying auto

        for attempt in range(1, MAX_CAPTCHA_ATTEMPTS + 1):
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

            # Run automated solver
            solved = await auto_solve_captcha(page, method=CAPTCHA_SOLVER)
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
                    except Exception:
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
        page = await self._new_page()

        try:
            await page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']", timeout=8000)
            if search_box:
                await search_box.fill(query)
                await asyncio.sleep(random.uniform(0.5, 1.2))
                await search_box.press("Enter")
                await page.wait_for_load_state("domcontentloaded")

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
                        break

                    # Wait for the page to finish navigating back to the search
                    # results after the CAPTCHA is cleared.
                    await asyncio.sleep(2.5)
                    try:
                        await page.wait_for_load_state("domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
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

        except Exception as exc:
            logger.error("Search error on query '%s': %s", query, exc)
        finally:
            await page.close()

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
            await page.close()

    async def _new_page(self, context: BrowserContext) -> Page:
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        return page

    async def run(self) -> None:
        logger.info("Starting Scraper execution...")
        async with async_playwright() as pw:
            user_data_dir = os.path.join(os.getcwd(), "browser_profile")
            context = await pw.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=HEADLESS,
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )

            google_scraper = GoogleScraper(context)

            # Step 1: Collect URLs across all queries and process incrementally
            for query in SEARCH_QUERIES:
                results = await google_scraper.search(query)
                logger.info("Query '%s' returned %d results.", query, len(results))

                # Step 2: Extract emails from snippets (always)
                for target in results:
                    self._process_target(target)

                # Step 3: Optionally visit URLs for deeper extraction
                if VISIT_URLS:
                    for target in results:
                        await self._visit_and_extract(context, target)

                # Step 4: Save incrementally after each query to avoid data loss
                if self.records:
                    dicts = [r.as_dict() for r in self.records]
                    save_to_csv(dicts)
                    save_to_gsheet(dicts)
                    logger.info("Saved %d record(s) after query '%s'.", len(dicts), query)
                    self.records.clear()  # avoid re-saving on next iteration

            logger.info("Scraping complete. Total unique emails: %d", len(self.global_seen_emails))

            await context.close()



if __name__ == "__main__":
    scraper = DataScraper()
    asyncio.run(scraper.run())