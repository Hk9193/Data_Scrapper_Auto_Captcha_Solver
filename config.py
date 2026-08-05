"""
config.py — Scraper Configuration
All tunable settings, search queries, and credentials live here.
"""

# ─── Search Queries ────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("New york") ("@gmail.com" OR "@outlook.com" OR "@yahoo.com")'
]

# ─── Pagination ────────────────────────────────────────────────────────────────
MAX_PAGES_PER_QUERY = 20       # Google pages to crawl per query
RESULTS_PER_PAGE    = 10       # Standard Google results per page

# ─── Scraping Strategy ─────────────────────────────────────────────────────────
VISIT_URLS = False             # Set to False to ONLY scrape Google Snippets (extremely fast)

# ─── Delays (seconds) ──────────────────────────────────────────────────────────
DELAY_MIN = 2.0
DELAY_MAX = 5.0
PAGE_LOAD_TIMEOUT   = 30_000  # ms — Playwright page.wait_for_load_state timeout
ELEMENT_TIMEOUT     = 10_000  # ms — short element wait

# ─── Concurrency ───────────────────────────────────────────────────────────────
MAX_TABS = 5   # Parallel page visits

# ─── Retries ───────────────────────────────────────────────────────────────────
MAX_RETRIES = 2

# ─── Browser ───────────────────────────────────────────────────────────────────
HEADLESS = False   # Set True for server / CI runs

# ─── CAPTCHA Solver ────────────────────────────────────────────────────────────
# "yolo"            — YOLOv8 image challenge only (recognizer)
# "audio"           — audio challenge + speech-to-text only
# "yolo_then_audio" — YOLO first, audio fallback (recommended)
CAPTCHA_SOLVER = "yolo"

# ─── Proxy / VPN ───────────────────────────────────────────────────────────────
# Leave PROXY_SERVER empty to use your system VPN / direct connection.
# Examples:
#   SOCKS5 (NordVPN, ProtonVPN proxy feature):
#       PROXY_SERVER = "socks5://127.0.0.1:1080"
#   HTTP proxy:
#       PROXY_SERVER = "http://proxy.example.com:8080"
#   Authenticated residential proxy (Bright Data, Smartproxy, Oxylabs):
#       PROXY_SERVER   = "http://brd.superproxy.io:22225"
#       PROXY_USERNAME = "your-username"
#       PROXY_PASSWORD = "your-password"
PROXY_SERVER   = ""   # e.g. "socks5://127.0.0.1:1080"
PROXY_USERNAME = ""   # leave empty if no auth needed
PROXY_PASSWORD = ""   # leave empty if no auth needed

# Rotate proxies: list multiple servers, scraper picks a random one per query.
# Leave empty list to use only PROXY_SERVER above.
PROXY_ROTATION_LIST: list[str] = [
    # "socks5://127.0.0.1:1080",
    # "socks5://127.0.0.1:1081",
    # "http://user:pass@proxy1.example.com:8080",
]

# ─── Link Expansion ────────────────────────────────────────────────────────────
EXPAND_LINKTREE  = True
EXPAND_EXTERNAL  = True
EXPANSION_DOMAINS = [
    "linktr.ee",
    "linkinbio",
    "beacons.ai",
    "bio.link",
    "allmylinks.com",
    "tap.bio",
    "solo.to",
]

# ─── Email Cleaning ────────────────────────────────────────────────────────────
EMAIL_BLACKLIST_KEYWORDS = [
    "noreply", "no-reply", "example", "test", "donotreply",
    "do-not-reply", "support@sentry", "notifications@", "mailer-daemon",
    "postmaster", "bounce", "@2x", ".png", ".jpg", ".gif",
]

# ─── Output ────────────────────────────────────────────────────────────────────
OUTPUT_CSV      = "results.csv"
OUTPUT_LOG      = "scraper.log"

# ─── Google Sheets (optional) ──────────────────────────────────────────────────
# Leave GSHEET_NAME empty to skip Google Sheets export
GSHEET_CREDENTIALS_FILE = "gsheet_credentials.json"   # Service account JSON
GSHEET_NAME             = ""                           # e.g. "DJ Leads"
GSHEET_WORKSHEET        = "Sheet1"

# ─── User-Agent Pool ───────────────────────────────────────────────────────────
USER_AGENTS = [
    # Chrome / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",

    # Firefox / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",

    # Chrome / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    # Safari / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",

    # Chrome / Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]
