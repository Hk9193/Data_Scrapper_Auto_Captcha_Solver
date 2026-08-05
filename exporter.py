"""
exporter.py — CSV and Google Sheets export
"""

import csv
import logging
import os
from typing import List, Dict, Any

from config import (
    OUTPUT_CSV,
    GSHEET_CREDENTIALS_FILE,
    GSHEET_NAME,
    GSHEET_WORKSHEET,
)

logger = logging.getLogger("scraper.exporter")

FIELDNAMES = [
    "username",
    "email",
    "source_url",
    "query_used",
    "found_in",
    "page_title",
]


# ─── CSV ───────────────────────────────────────────────────────────────────────

def save_to_csv(records: List[Dict[str, Any]], path: str = OUTPUT_CSV) -> None:
    """Append *records* to CSV, creating headers if the file is new."""
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerows(records)
    logger.info("CSV  ← %d record(s) appended to %s", len(records), path)


def load_csv(path: str = OUTPUT_CSV) -> List[Dict[str, str]]:
    """Read all rows from CSV (used for deduplication across runs)."""
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ─── Google Sheets ─────────────────────────────────────────────────────────────

def save_to_gsheet(records: List[Dict[str, Any]]) -> None:
    """Push *records* to a Google Sheet (service-account auth)."""
    if not GSHEET_NAME:
        logger.debug("GSHEET_NAME not configured — skipping Sheets export.")
        return

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(
            GSHEET_CREDENTIALS_FILE, scopes=scopes
        )
        gc   = gspread.authorize(creds)
        sh   = gc.open(GSHEET_NAME)
        ws   = sh.worksheet(GSHEET_WORKSHEET)

        # Ensure header row exists
        existing = ws.get_all_values()
        if not existing:
            ws.append_row(FIELDNAMES)

        rows = [
            [str(rec.get(f, "")) for f in FIELDNAMES]
            for rec in records
        ]
        ws.append_rows(rows, value_input_option="USER_ENTERED")
        logger.info("Sheets ← %d row(s) appended to '%s'", len(rows), GSHEET_NAME)

    except ImportError:
        logger.warning("gspread not installed — skipping Sheets export.")
    except Exception as exc:
        logger.error("Google Sheets export failed: %s", exc)
