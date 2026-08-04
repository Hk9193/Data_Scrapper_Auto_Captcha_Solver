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

from captcha_solver import auto_solve_captcha
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
                if "/sorry/index" in page.url:
                    logger.critical("GOOGLE CAPTCHA DETECTED! Running automated solver...")
                    solved = await auto_solve_captcha(page, method=CAPTCHA_SOLVER)
                    if not solved:
                        logger.warning("Automated solve attempt finished. Waiting for manual solve in open browser...")
                        while "/sorry/index" in page.url:
                            await asyncio.sleep(3)
                        logger.info("CAPTCHA solved! Resuming search...")


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


class DJScraper:
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
            
            # Step 1: Collect URLs across all queries
            search_targets: List[Dict[str, str]] = []
            for query in SEARCH_QUERIES:
                results = await google_scraper.search(query)
                search_targets.extend(results)

            logger.info("Extracted %d total URLs to process.", len(search_targets))

            # Step 2: Save accumulated results
            if self.records:
                dicts = [r.as_dict() for r in self.records]
                save_to_csv(dicts)
                save_to_gsheet(dicts)

            await context.close()



if __name__ == "__main__":
    scraper = DJScraper()
    asyncio.run(scraper.run())