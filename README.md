# DJ Email & Instagram Scraper 🎧

A production-grade **async Playwright (Python)** scraper that extracts DJ Instagram usernames and emails from Google search results — including emails buried inside page comments.

---

## Features

| Feature | Details |
|---|---|
| 🔍 Google Search | Paginated (up to 10 pages per query) |
| 📧 Email Extraction | Snippet · Page body · Comments · Expansion links |
| 📸 Instagram Usernames | Extracted from URLs |
| 💬 Comment Scraping | YouTube, generic CMS (Disqus, WordPress, etc.) |
| 🔗 Link Expansion | Linktree, Beacons, bio.link, and more |
| 🤖 Anti-Detection | User-agent rotation, random delays, visible browser |
| ⚡ Async Concurrency | 5 tabs max (configurable) |
| 💾 Export | CSV + optional Google Sheets |
| 🔁 Resumable | Skips already-seen emails across runs |

---

## Project Structure

```
EmailScrapper/
├── scraper.py          # Main async orchestrator
├── config.py           # All settings + search queries
├── utils.py            # Regex, cleaning, deduplication
├── exporter.py         # CSV + Google Sheets writer
├── logger_setup.py     # Coloured console + rotating file log
├── requirements.txt    # Python dependencies
├── results.csv         # Output (auto-created)
└── scraper.log         # Log file (auto-created)
```

---

## Setup

### 1. Prerequisites
- **Python 3.10+** required
- Windows / macOS / Linux

### 2. Create & activate a virtual environment

```powershell
# Windows PowerShell
cd d:\EmailScrapper
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
playwright install chromium
```

---

## Configuration

Edit **`config.py`** before running:

### Search queries
```python
SEARCH_QUERIES = [
    "DJ booking email contact site:instagram.com",
    "DJ producer email booking gmail.com",
    # Add your own queries here...
]
```

### Key settings

| Setting | Default | Description |
|---|---|---|
| `MAX_PAGES_PER_QUERY` | `10` | Google pages per query |
| `HEADLESS` | `False` | `True` = invisible browser |
| `MAX_TABS` | `5` | Concurrent page visits |
| `DELAY_MIN / MAX` | `2.0 / 5.0` | Random delay range (seconds) |
| `MAX_RETRIES` | `2` | Retries on page failure |
| `EXPAND_LINKTREE` | `True` | Follow bio-aggregator links |

### Email blacklist
Words in `EMAIL_BLACKLIST_KEYWORDS` will cause emails to be discarded (noreply, test, example, etc.).

---

## Google Sheets Setup (Optional)

1. Create a **Google Cloud Service Account** and download the JSON credentials file.
2. Share your target Google Sheet with the service account email.
3. Place the JSON file in `d:\EmailScrapper\` and update `config.py`:

```python
GSHEET_CREDENTIALS_FILE = "gsheet_credentials.json"
GSHEET_NAME             = "DJ Leads"        # Name of your spreadsheet
GSHEET_WORKSHEET        = "Sheet1"
```

If `GSHEET_NAME` is left empty (`""`), Google Sheets export is skipped.

---

## Running

```powershell
# From d:\EmailScrapper with venv activated:
python scraper.py
```

### What you'll see
```
13:00:00 [INFO    ] ============================================================
13:00:00 [INFO    ] DJ Email Scraper  — starting
13:00:00 [INFO    ] Queries : 10  |  Max pages: 10  |  Max tabs: 5
13:00:00 [INFO    ] ============================================================

13:00:00 [INFO    ] >>> Query: DJ booking email contact site:instagram.com
13:00:02 [INFO    ] Google search p1/10  →  DJ booking email contact ...
13:00:07 [INFO    ]   [page]  https://example.com → 3 email(s)
13:00:09 [INFO    ]   [comments] https://example.com → 1 email(s)
13:00:12 [INFO    ]   [expand] Following → https://linktr.ee/djexample
```

---

## Output — `results.csv`

| Column | Description |
|---|---|
| `username` | Instagram username (e.g. `djexample`) |
| `email` | Email address |
| `source_url` | Page where email was found |
| `query_used` | Google query that led to this result |
| `found_in` | `snippet` / `page` / `comment` / `expansion` |
| `page_title` | Title of the source page |

---

## Resuming / Re-running

The scraper **automatically deduplicates** against `results.csv` between runs. Emails already saved will not be re-added.

---

## Anti-blocking Tips

- Keep `HEADLESS = False` to look more like a real browser.
- Increase `DELAY_MIN` / `DELAY_MAX` if Google starts showing CAPTCHAs.
- Add a Google account cookie by logging in manually (the browser window stays open).
- Reduce `MAX_PAGES_PER_QUERY` to scrape less aggressively.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `playwright install` fails | Run as administrator |
| Google CAPTCHA appears | Solve it manually in the open browser window, scraper will continue |
| `colorlog` not found | `pip install colorlog` |
| Sheets auth error | Check service account email has edit access to the sheet |
