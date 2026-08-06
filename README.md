# Data Scraper 🕵️

A production-grade **async Playwright (Python)** scraper for **sales and lead generation**. It scrapes business data — **emails, contacts, owners, and more** — directly from Google search results, targeting business owners, founders, CEOs, and entrepreneurs (e.g. LinkedIn profiles with personal email addresses such as Gmail, Outlook, Hotmail, Yahoo).

---

## Features

| Feature | Details |
|---|---|
| 🔍 Google Search | Paginated (up to 20 pages per query) |
| 📧 Email Extraction | Snippet-based extraction (fast mode) or full page scraping |
| 🤖 CAPTCHA Solving | YOLOv8 image solver + audio fallback (Speech-to-Text) |
| 🌐 Anti-Detection | User-agent rotation, stealth mode, random delays, visible browser |
| 🔁 Proxy Support | Optional proxy rotation per query |
| 💾 Export | CSV + optional Google Sheets |
| 🔄 Resumable | Skips already-seen emails across runs |
| 🧩 Persistent Profile | Reuses browser session/cookies across runs |

---

## Project Structure

```
EmailScrapper/
├── scraper.py            # Main async orchestrator
├── config.py             # All settings + search queries
├── utils.py              # Regex, cleaning, deduplication, delays
├── exporter.py           # CSV + Google Sheets writer
├── captcha_solver.py     # Automated reCAPTCHA solver (YOLOv8 + audio)
├── logger_setup.py       # Coloured console + rotating file log
├── check_model.py        # YOLOv8 model verification script
├── test_stealth.py       # Playwright stealth test script
├── requirements.txt      # Python dependencies
├── googlequeries.txt     # Alternative search queries (reference)
├── yolov8m-seg.pt        # YOLOv8 segmentation model weights (CAPTCHA solver)
├── results.csv           # Output (auto-created)
├── scraper.log           # Log file (auto-created)
└── browser_profile/      # Persistent Chromium profile (auto-created)
```

---

## Setup

### 1. Prerequisites
- **Python 3.10+** required (tested on Python 3.12)
- Windows / macOS / Linux

### 2. Create & activate a virtual environment

```powershell
# Windows PowerShell
cd EmailScrapper
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
playwright install chromium
```

> **Note:** The CAPTCHA solver uses `ultralytics` (YOLOv8) which installs `torch` and `torchvision` automatically. The model weights file `yolov8m-seg.pt` is included in the repo.

---

## Configuration

Edit **`config.py`** before running:

### Search queries
The scraper comes pre-configured with 30 LinkedIn search queries targeting business owners, founders, and CEOs across various UK cities:

```python
SEARCH_QUERIES = [
    'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Milton Keynes") ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
    'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Reading") ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
    # ... 28 more queries for UK cities
]
```

> See `googlequeries.txt` for additional example queries.

### Key settings

| Setting | Default | Description |
|---|---|---|
| `MAX_PAGES_PER_QUERY` | `20` | Google pages to crawl per query |
| `RESULTS_PER_PAGE` | `10` | Standard Google results per page |
| `VISIT_URLS` | `False` | `False` = snippet-only mode (fast); `True` = visit each page |
| `HEADLESS` | `False` | `True` = invisible browser |
| `MAX_TABS` | `5` | Concurrent page visits |
| `DELAY_MIN / MAX` | `2.0 / 5.0` | Random delay range (seconds) |
| `PAGE_LOAD_TIMEOUT` | `30000` | Page load timeout (ms) |
| `ELEMENT_TIMEOUT` | `10000` | Element wait timeout (ms) |
| `MAX_RETRIES` | `2` | Retries on page failure |
| `CAPTCHA_SOLVER` | `"yolo"` | CAPTCHA method: `yolo`, `audio`, or `yolo_then_audio` |
| `EXPAND_LINKTREE` | `True` | Follow bio-aggregator links |
| `EXPAND_EXTERNAL` | `True` | Follow external expansion links |

### CAPTCHA Solver

The scraper includes an automated Google reCAPTCHA solver with two methods:

| Method | Description |
|---|---|
| `yolo` | YOLOv8 image challenge solver (recognizer library) — handles 3×3 / 4×4 image grids |
| `audio` | Audio challenge + Google Speech Recognition fallback |
| `yolo_then_audio` | YOLO first, audio fallback (recommended for reliability) |

If automated solving fails, the scraper waits for **manual solve** in the open browser window, then automatically resumes.

### Proxy / VPN

Leave `PROXY_SERVER` empty to use your system VPN / direct connection:

```python
PROXY_SERVER   = ""   # e.g. "socks5://127.0.0.1:1080"
PROXY_USERNAME = ""   # leave empty if no auth needed
PROXY_PASSWORD = ""   # leave empty if no auth needed

# Rotate proxies: scraper picks a random one per query
PROXY_ROTATION_LIST = [
    # "socks5://127.0.0.1:1080",
    # "http://user:pass@proxy1.example.com:8080",
]
```

### Email blacklist
Words in `EMAIL_BLACKLIST_KEYWORDS` will cause emails to be discarded (noreply, test, example, etc.). Emails ending in image/video extensions (`.png`, `.jpg`, `.mp4`, etc.) are also filtered.

---

## Google Sheets Setup (Optional)

1. Create a **Google Cloud Service Account** and download the JSON credentials file.
2. Share your target Google Sheet with the service account email.
3. Place the JSON file in the project root and update `config.py`:

```python
GSHEET_CREDENTIALS_FILE = "gsheet_credentials.json"
GSHEET_NAME             = "Sales Leads"     # Name of your spreadsheet
GSHEET_WORKSHEET        = "Sheet1"
```

If `GSHEET_NAME` is left empty (`""`), Google Sheets export is skipped.

---

## Running

```powershell
# From project root with venv activated:
python scraper.py
```

### What you'll see
```
14:32:08 [INFO    ] Starting Scraper execution...
14:32:14 [CRITICAL] GOOGLE CAPTCHA DETECTED! Running automated solver...
14:33:55 [INFO    ] Attempting YOLOv8 image reCAPTCHA solve (recognizer) — attempt 1/3...
14:35:07 [WARNING ] YOLOv8 reCAPTCHA solve error on attempt 1/3: Invisible reCaptcha Timed Out.
14:37:46 [WARNING ] Automated solve attempt finished. Waiting for manual solve in open browser...
14:37:46 [INFO    ] CAPTCHA solved! Resuming search...
```

> **Important:** Google frequently shows CAPTCHAs during automated searches. If the YOLOv8 solver fails, solve the CAPTCHA manually in the browser window — the scraper will detect this and resume automatically.

---

## Output — `results.csv`

| Column | Description |
|---|---|
| `username` | Username / handle (if found in URL/text; e.g. Instagram or social handle) |
| `email` | Email address extracted from snippet or page |
| `source_url` | Source URL where the data was found (e.g. LinkedIn profile, business website) |
| `page_title` | Title of the source page (e.g. LinkedIn profile headline, business name) |

---

## Utility Scripts

### `check_model.py`
Verifies the YOLOv8 model loads correctly and prints available classes:
```powershell
python check_model.py
```

### `test_stealth.py`
Tests Playwright stealth plugin functionality:
```powershell
python test_stealth.py
```

---

## Resuming / Re-running

The scraper **automatically deduplicates** against `results.csv` between runs. Emails already saved will not be re-added.

> **Note:** The persistent browser profile (`browser_profile/`) retains cookies and session data. If you get a "profile already in use" error, ensure no other instance of the scraper is running, or delete the `browser_profile/` directory to start fresh.

---

## Anti-blocking Tips

- Keep `HEADLESS = False` to look more like a real browser.
- Increase `DELAY_MIN` / `DELAY_MAX` if Google starts showing CAPTCHAs frequently.
- Add a Google account cookie by logging in manually (the browser window stays open).
- Reduce `MAX_PAGES_PER_QUERY` to scrape less aggressively.
- Use `PROXY_ROTATION_LIST` to distribute requests across multiple IPs.
- Switch VPN or use a mobile hotspot if Google blocks your IP (audio CAPTCHA "Try again later" message).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `playwright install` fails | Run as administrator |
| Google CAPTCHA appears | Solve it manually in the open browser window, scraper will continue |
| `colorlog` not found | `pip install colorlog` |
| Sheets auth error | Check service account email has edit access to the sheet |
| "Profile already in use" error | Close any running scraper instances or delete `browser_profile/` |
| YOLOv8 solver times out | Switch `CAPTCHA_SOLVER` to `"yolo_then_audio"` or solve manually |
| Audio CAPTCHA "Try again later" | Google has IP-blocked audio challenges — switch VPN/IP or use YOLO image solver |
| `recognizer` not installed | `pip install recognizer` |
| `Invisible reCaptcha Timed Out` | Google served an invisible reCAPTCHA — solve manually in browser |