"""
config.py — Scraper Configuration
All tunable settings, search queries, and credentials live here.
"""

# ─── Search Queries ────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Amravati") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sangli") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bhubaneswar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Cuttack") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Rourkela") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Berhampur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sambalpur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Balasore") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Puri") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ludhiana") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Amritsar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Jalandhar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Mohali") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Patiala") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bathinda") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Pathankot") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Jaipur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Jodhpur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Udaipur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kota") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ajmer") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bikaner") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Alwar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bhiwadi") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Chennai") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Coimbatore") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Madurai") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Tiruchirappalli" OR Trichy) (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Salem") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Tiruppur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Erode") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Vellore") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Thoothukudi" OR Tuticorin) (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Tirunelveli") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Hosur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Hyderabad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Warangal") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Nizamabad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Karimnagar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Khammam") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ramagundam") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kolkata") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Siliguri") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Asansol") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Durgapur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Howrah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kharagpur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bardhaman") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Haldia") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Lucknow") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Noida") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ghaziabad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kanpur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Agra") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Varanasi") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Prayagraj") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Meerut") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bareilly") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Gorakhpur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Mathura") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Moradabad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Aligarh") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Saharanpur") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

]

# ─── Pagination ────────────────────────────────────────────────────────────────
MAX_PAGES_PER_QUERY = 15       # Google pages to crawl per query
RESULTS_PER_PAGE    = 20       # Standard Google results per page

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
#
# NOTE: keep "yolo_then_audio" so an unsolvable image grid has a second,
# independent solution path. This is a key part of ensuring a CAPTCHA
# can never permanently block the scraper.
CAPTCHA_SOLVER = "yolo_then_audio"

# ─── Reliability / 24-7 Operation ──────────────────────────────────────────────
# These settings make the scraper run continuously until manually stopped, and
# guarantee that a hung browser / unsolvable CAPTCHA can NOT permanently stop it.

# Run forever (restart cycles until the process is manually stopped / Ctrl+C).
# Set False to run a single pass over SEARCH_QUERIES (legacy behaviour).
CONTINUOUS_MODE = True

# Hard wall-clock budget (seconds) that a SINGLE CAPTCHA-solving session may
# consume before we give up on it, take a cooldown, relaunch the browser for a
# fresh session/IP, and move on to the next query. Prevents the hours-long
# "death spiral" seen in the logs (each YOLO attempt alone was ~3–10 min).
MAX_CAPTCHA_SOLVE_SECONDS = 240

# Pause (seconds) after a query is blocked by an unsolvable CAPTCHA, before the
# browser is relaunched and we continue with the SAME query.
CAPTCHA_COOLDOWN_SECONDS = 20

# Maximum number of recovery attempts for a SINGLE query before we give up on
# it and move on to the next query. Prevents a permanently broken query from
# looping forever, while still retrying the SAME query (not skipping it) after
# every CAPTCHA / browser / timeout recovery.
MAX_QUERY_CAPTCHA_RETRIES = 5

# Absolute ceiling (seconds) for processing ONE query (search + visit + save).
# Wraps the whole query in asyncio.wait_for so that a Playwright call which
# hangs forever waiting on a dead browser can never freeze the process — it is
# forced to raise, we recreate the browser, and continue.
QUERY_PROCESS_TIMEOUT_SECONDS = 900

# Recycle the browser/context after this many query passes to prevent
# memory/handle leaks that accumulate over hours of continuous operation.
# Set to 0 to disable recycling (legacy behaviour).
BROWSER_RECYCLE_QUERIES = 10

# Extra pause (seconds) after a full cycle in which every query hit a
# CAPTCHA/blocked wall — gives IP/UA rotation a chance before the next
# cycle starts over with the same likely-blocked session.
CYCLE_BLOCKED_COOLDOWN_SECONDS = 60

# Delay (seconds) between continuous-mode cycles after a graceful cycle end.
CYCLE_RESTART_DELAY = 10

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
GSHEET_NAME             = ""                           # e.g. "Sales Leads"
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
