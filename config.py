"""
config.py — Scraper Configuration
All tunable settings, search queries, and credentials live here.
"""

import os
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


# ─── Search Queries ────────────────────────────────────────────────────────────
SEARCH_QUERIES = [
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Stockholm") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Gothenburg" OR "Göteborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Malmö" OR "Malmo") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Uppsala") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Västerås" OR "Vasteras") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Örebro" OR "Orebro") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Linköping" OR "Linkoping") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Helsingborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Jönköping" OR "Jonkoping") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Norrköping" OR "Norrkoping") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Lund") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Umeå" OR "Umea") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Gävle" OR "Gavle") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Borås" OR "Boras") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Södertälje" OR "Sodertalje") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Eskilstuna") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Halmstad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Växjö" OR "Vaxjo") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Karlstad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sundsvall") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Östersund" OR "Ostersund") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Trollhättan" OR "Trollhattan") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Luleå" OR "Lulea") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Borlänge" OR "Borlange") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kalmar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kristianstad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Skellefteå" OR "Skelleftea") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Falun") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Karlskrona") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Nyköping" OR "Nykoping") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Uddevalla") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Motala") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Landskrona") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Örnsköldsvik" OR "Ornskoldsvik") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Vänersborg" OR "Vanersborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Trelleborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Varberg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kiruna") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Visby") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kungsbacka") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Copenhagen" OR "København") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Aarhus" OR "Århus") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Odense") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Aalborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Esbjerg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Randers") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kolding") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Horsens") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Vejle") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Roskilde") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Herning") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Silkeborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Næstved" OR "Naestved") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Fredericia") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Viborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Køge" OR "Koge") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Holstebro") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Taastrup") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Slagelse") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Hillerød" OR "Hillerod") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sønderborg" OR "Sonderborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Svendborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Hjørring" OR "Hjorring") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Frederikshavn") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Helsingør" OR "Helsingor") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ringsted") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Haderslev") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Skive") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Nykøbing Falster" OR "Nykobing Falster") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kalundborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',

'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Oslo") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bergen") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Trondheim") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Stavanger") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Drammen") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Fredrikstad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kristiansand") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sandnes") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Tromsø" OR "Tromso") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sarpsborg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Skien") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Ålesund" OR "Alesund") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Sandefjord") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Haugesund") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Tønsberg" OR "Tonsberg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Moss") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Porsgrunn") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Bodø" OR "Bodo") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Arendal") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Hamar") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Larvik") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Halden") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Kongsberg") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Gjøvik" OR "Gjovik") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Lillehammer") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Molde") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Harstad") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Alta") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Narvik") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
'site:linkedin.com/in ("business owner" OR founder OR CEO OR entrepreneur) ("Steinkjer") (mail OR contact) ("@gmail.com" OR "@outlook.com" OR "@hotmail.com" OR "@yahoo.com")',
]

# ─── Pagination ────────────────────────────────────────────────────────────────
MAX_PAGES_PER_QUERY = 15       # Google pages to crawl per query
RESULTS_PER_PAGE    = 15       # Standard Google results per page

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
# Keep User-Agents consistent with host platform (Windows 10/11) to avoid
# navigator.userAgentData / Client Hints fingerprint mismatches that trigger bot walls.
USER_AGENTS = [
    # Chrome on Windows 10/11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    # Microsoft Edge on Windows 10/11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",

    # Firefox on Windows 10/11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]
