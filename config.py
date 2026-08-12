"""
config.py — Scraper Configuration
All tunable settings, search queries, and credentials live here.
"""

# ─── Search Queries ────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Dubai") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Deira") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bur Dubai") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Jumeirah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Barsha") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Business Bay") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Dubai Marina") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Jebel Ali") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Quoz") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Downtown Dubai") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Abu Dhabi") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Ain") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Madinat Zayed") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ruwais") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ghayathi") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Liwa") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Mirfa") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sila") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sharjah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Khor Fakkan") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kalba") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Dibba Al-Hisn") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Dhaid") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Madam") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Hamriyah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ajman") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Masfout") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Manama") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Umm Al Quwain") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Falaj Al Mualla") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ras Al Khaimah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Rams") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Dhayah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Fujairah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Dibba Al-Fujairah" OR "Dibba") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Al Badiyah") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Masafi") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

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

# ─── Traffic Management / Rate Limiting ────────────────────────────────────────
# Google flags high-volume automated traffic with CAPTCHA / unusual-traffic
# walls. We reduce unnecessary requests with a global rate limiter applied to
# EVERY Google navigation (homepage load, search submit, each pagination click)
# plus exponential backoff with jitter on retries. These limits are shared
# across all tabs/cycles so concurrent tasks never cause a request burst.
REQUEST_MIN_INTERVAL_SECONDS = 6.0    # min gap between two Google requests
REQUEST_WINDOW_SECONDS       = 60     # sliding window used for the cap below
MAX_REQUESTS_PER_WINDOW      = 10     # max Google requests allowed per window

# Base/max for jittered exponential backoff before retrying Google after a
# transient error / browser death / timeout (grows by 2x each attempt).
BACKOFF_BASE_SECONDS = 30
BACKOFF_MAX_SECONDS  = 900
# Slightly longer backoff used after Google has served a CAPTCHA block, so we
# give the network/IP a real chance to cool down before we touch it again.
CAPTCHA_BACKOFF_BASE_SECONDS = 60
CAPTCHA_BACKOFF_MAX_SECONDS  = 1800

# Do not re-crawl a query that already fully completed within this many
# seconds. This stops every continuous cycle from re-requesting the exact same
# queries (the #1 source of duplicate Google traffic).
QUERY_CACHE_INTERVAL_SECONDS = 3600

# Persisted scraper state file: maps each query -> last fully-extracted page +
# the wall-clock time it was completed, so the scraper can pause/resume and skip
# already-done queries across restarts.
STATE_FILE = "scraper_state.json"

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

# Seconds to wait for a HUMAN to solve a CAPTCHA in the visible browser after
# the automated solver fails, before re-running the automated solver. In
# unattended 24/7 mode set this low (e.g. 8-15s) because each wait is pure dead
# time repeating MAX_CAPTCHA_ATTEMPTS times per query. Increase it if you run
# with a human present who will manually solve challenges.
CAPTCHA_MANUAL_WAIT_SECONDS = 15

# Maximum number of recovery attempts for a SINGLE query before we give up on
# it and move on to the next query. Prevents a permanently broken query from
# looping forever, while still retrying the SAME query (not skipping it) after
# every CAPTCHA / browser / timeout recovery.
MAX_QUERY_CAPTCHA_RETRIES = 5

# ─── Google Automated-Query Rate Limit ─────────────────────────────────────────
# Google sometimes stops answering with a reCAPTCHA and instead serves a PLAIN
# text wall — "Try again later." / "Your computer or network may be sending
# automated queries." — with NO checkbox / image / audio challenge to solve.
# That is a HARD rate limit, NOT a CAPTCHA, so we never spend the YOLO/retry
# budget on it. Instead the scraper applies a bounded exponential backoff and
# periodically probes whether Google is usable again, resuming the exact
# pending query/page once it is.
#
# Initial cooldown (seconds) before the first availability re-check.
GOOGLE_BLOCK_COOLDOWN_SECONDS = 60
# Backoff doubles after every failed probe, capped at this many seconds.
GOOGLE_BLOCK_BACKOFF_MAX_SECONDS = 900
# Maximum number of availability probes before the worker pauses/exits
# (rather than burning retries against a still-hard-blocked Google).
GOOGLE_BLOCK_MAX_CHECKS = 10

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
