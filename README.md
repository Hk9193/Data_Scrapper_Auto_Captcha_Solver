# Data Scraper 🕵️

A production-grade **async Playwright (Python)** scraper for **sales and lead generation**. It scrapes business data — **emails, contacts, owners, and more** — directly from Google search results, targeting business owners, founders, CEOs, and entrepreneurs (e.g. LinkedIn profiles with personal email addresses such as Gmail, Outlook, Hotmail, Yahoo).

---

## Features

| Feature | Details |
|---|---|
| 🔍 Google Search | Paginated (up to 20 pages per query) |
| 📧 Email Extraction | Snippet-based extraction (fast mode) or full page scraping |
| 🤖 CAPTCHA Solving | **YOLOv8 / YOLO 11** image solver + audio fallback (Speech-to-Text) |
| 🧠 Humanized Solving | Per-session behavior profiles (Fast/Normal/Careful) with randomized timing, mouse movement & per-tile delays |
| 🌐 Anti-Detection | User-agent rotation, stealth mode, random delays, visible browser |
| 🔁 Proxy Support | Optional proxy rotation per query |
| 💾 Export | CSV + optional Google Sheets |
| 🔄 Resumable | Skips already-seen emails across runs |
| 🧩 Persistent Profile | Reuses browser session/cookies across runs |

---

## Project Structure

```
Data_Scrapper_Auto_Captcha_Solver/
├── scraper.py            # Main async orchestrator
├── config.py             # All settings + search queries
├── utils.py              # Regex, cleaning, deduplication, delays
├── exporter.py           # CSV + Google Sheets writer
├── captcha_solver.py     # Automated reCAPTCHA solver (YOLOv8/YOLO 11 + audio)
├── human_behavior.py     # Human-like CAPTCHA session profiles & timing randomization
├── logger_setup.py       # Coloured console + rotating file log
├── check_model.py        # YOLO model verification script (v8 + v11)
├── test_stealth.py       # Playwright stealth test script
├── requirements.txt      # Python dependencies
├── googlequeries.txt     # Alternative search queries (reference)
├── yolov8m-seg.pt        # YOLOv8 segmentation model weights (CAPTCHA solver)
├── yolo11m-seg.pt        # YOLO 11 segmentation model weights (CAPTCHA solver)
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
cd Data_Scrapper_Auto_Captcha_Solver
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
playwright install chromium
```

> **Note:** The CAPTCHA solver uses `ultralytics` (YOLOv8 / YOLO 11) which installs `torch` and `torchvision` automatically. Both model weight files (`yolov8m-seg.pt` and `yolo11m-seg.pt`) are included in the repo.

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

> See `googlequeries.txt` for additional example queries (e.g. Instagram-based DJ/booking queries).

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
| `yolo` | **YOLOv8 / YOLO 11** image challenge solver (recognizer library) — handles 3×3 / 4×4 image grids |
| `audio` | Audio challenge + Google Speech Recognition fallback |
| `yolo_then_audio` | YOLO first, audio fallback (recommended for reliability) |

The CAPTCHA solver uses the **recognizer** library (Vinyzu) which leverages **ultralytics YOLO** models. Both **YOLOv8** (`yolov8m-seg.pt`) and **YOLO 11** (`yolo11m-seg.pt`) segmentation model weights are included in the repo. The recognizer library automatically detects the best available model for image classification challenges (buses, traffic lights, crosswalks, bicycles, etc.).

If automated solving fails, the scraper waits for **manual solve** in the open browser window, then automatically resumes.

### Humanized CAPTCHA Solving

Every CAPTCHA session generates a fresh **HumanBehavior profile** (`human_behavior.py`) that makes each solve behave differently:

- **Behaviour Profiles**: `Fast` / `Normal` / `Careful` — randomly chosen per session
- **Mouse Speed**: `Fast` / `Medium` / `Slow` — randomly chosen per session
- **Maximum YOLO Attempts**: random integer between **3 and 10** per session
- **Maximum Retries**: random integer between **15 and 25** per session
- **Randomized Timing**: every pause (before checkbox, before verify, after reload, etc.) is regenerated independently
- **Human Mouse Behavior**: hesitation, micro-pauses, ±2-8px cursor offsets, and overshoot correction before every tile click
- **Per-Tile Delays**: fresh random delay between each tile click (e.g. 2.18s, 4.61s, 3.22s...)
- **Verify Pause**: 2-6 seconds before pressing Verify (as if checking selected tiles)
- **Reload Pause**: random 1.5-5s before pressing reload, plus additional wait after

When a CAPTCHA session starts, the scraper logs:
```
==================================================
CAPTCHA Session Started
Behaviour Profile: Careful
Maximum YOLO Attempts: 8
Maximum Retries: 19
Mouse Speed: Medium
==================================================
```

This module **does not modify** the recognizer library. It subclasses `AsyncChallenger` to wrap human behavior around the existing YOLO detection pipeline.

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
14:32:14 [INFO    ] ==================================================
14:32:14 [INFO    ] CAPTCHA Session Started
14:32:14 [INFO    ] Behaviour Profile: Careful
14:32:14 [INFO    ] Maximum YOLO Attempts: 8
14:32:14 [INFO    ] Maximum Retries: 19
14:32:14 [INFO    ] Mouse Speed: Medium
14:32:14 [INFO    ] ==================================================
14:33:55 [INFO    ] Attempting YOLOv8 image reCAPTCHA solve (recognizer) — attempt 1/8...
14:35:07 [WARNING ] YOLOv8 reCAPTCHA solve error on attempt 1/8: Invisible reCaptcha Timed Out.
14:37:46 [WARNING ] Automated solve attempt finished. Waiting for manual solve in open browser...
14:37:46 [INFO    ] CAPTCHA solved! Resuming search...
```

> **Important:** Google frequently shows CAPTCHAs during automated searches. If the YOLO solver fails, solve the CAPTCHA manually in the browser window — the scraper will detect this and resume automatically.

---

## Output — `results.csv`

| Column | Description |
|---|---|
| `username` | Username / handle (if found in URL/text; e.g. Instagram or social handle) |
| `email` | Email address extracted from snippet or page |
| `source_url` | Source URL where the data was found (e.g. LinkedIn profile, business website) |
| `query_used` | The search query that produced this result |
| `found_in` | Where the data was found (`google_snippet` or `page_content`) |
| `page_title` | Title of the source page (e.g. LinkedIn profile headline, business name) |

---

## Utility Scripts

### `check_model.py`
Verifies the YOLO model loads correctly and prints available classes. Supports both **YOLOv8** and **YOLO 11**:
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
| YOLO solver times out | Switch `CAPTCHA_SOLVER` to `"yolo_then_audio"` or solve manually |
| Audio CAPTCHA "Try again later" | Google has IP-blocked audio challenges — switch VPN/IP or use YOLO image solver |
| `recognizer` not installed | `pip install recognizer` |
| `Invisible reCaptcha Timed Out` | Google served an invisible reCAPTCHA — solve manually in browser |

## How CAPTCHA Solver works

The CAPTCHA solver is an automated solution that uses artificial intelligence to solve Google reCAPTCHA challenges. Here's how it works:

1. **YOLOv8/YOLO 11 image solver** - The solver uses YOLOv8/YOLO 11 image classification models to detect and classify objects in the CAPTCHA image.
2. **Audio solver** - The solver uses audio recognition to solve audio CAPTCHAs.
3. **yolo_then_audio** - The solver uses YOLOv8/YOLO 11 image classification models to detect and classify objects in the CAPTCHA image, and if that fails, it uses audio recognition to solve audio CAPTCHAs.

Process 
## Complete CAPTCHA Solver Flow — How It Works

Here's the complete end-to-end flow of how the CAPTCHA solver detects and solves Google reCAPTCHA:

---

### Step 1: CAPTCHA Detection (in `scraper.py`)

```
Google search page → URL contains "/sorry/index" → CAPTCHA DETECTED
```

The scraper checks the page URL after each Google search. If Google redirects to `/sorry/index`, it means a CAPTCHA challenge was triggered. The scraper then calls `auto_solve_captcha(page, method="yolo")`.

---

### Step 2: Solver Selection (in `captcha_solver.py`)

```
auto_solve_captcha(page, method="yolo")
  └── HumanBehavior.create()  →  Fresh profile per session
  └── solve_recaptcha_yolo(page, behavior)
```

The `auto_solve_captcha` function generates a fresh **HumanBehavior** profile (thinking profile, mouse speed, YOLO attempts 3-10, retries 15-25) and dispatches to the YOLO image solver (configured via `CAPTCHA_SOLVER = "yolo"` in `config.py`). It tries up to the session's random attempt count because Google sometimes re-serves a fresh grid even after a correct selection.

---

### Step 3: Initialize the Challenger (in `human_behavior.py` → `recognizer/agents/playwright/async_control.py`)

```python
challenger = HumanizedAsyncChallenger(page, human_behavior=behavior)
```

This creates a `HumanizedAsyncChallenger` that **subclasses** recognizer's `AsyncChallenger` (source untouched) and:
- Loads the **YOLO11 segmentation model** (`yolo11m-seg.pt`) and **CLIP/CLIPSeg models** for image understanding
- Sets up a **route interceptor** to monitor Google's reCAPTCHA API calls (`reload` and `userverify` endpoints)
- The route handler detects if the challenge is **dynamic** (keeps refreshing tiles) and captures the **CAPTCHA token** when solved
- Adds human-like timing, mouse movement, and per-tile delays around the detection pipeline

---

### Step 4: Click the Checkbox (in `solve_recaptcha()`)

```python
# Human pause before clicking checkbox (0.7-2.8s profile-adjusted)
await asyncio.sleep(behavior.delay("before_checkbox"))
await self.click_checkbox()   # Clicks "I'm not a robot" checkbox
```

The solver finds the reCAPTCHA checkbox iframe (`iframe[title='reCAPTCHA']`) and clicks the `.recaptcha-checkbox-border` element. This either:
- **Passes** the CAPTCHA (no challenge needed) → returns the token immediately
- **Triggers** a visual challenge (image grid) → proceeds to Step 5

---

### Step 5: Load the Challenge (in `load_captcha()`)

```python
# Checks if the bframe (challenge iframe) is visible
if not await self.check_captcha_visible():
    if captcha_token := await self.check_result():
        return captcha_token
    elif not await self.click_checkbox():
        raise TypedTimeoutError("Invisible reCaptcha Timed Out.")
```

The solver:
1. Waits for the **bframe iframe** (the challenge frame) to become visible
2. If no challenge appears, checks if a CAPTCHA token was already obtained
3. If the checkbox click didn't trigger a challenge, retries

---

### Step 6: Read the Challenge Prompt (in `handle_recaptcha()`)

```python
captcha_frame = self.page.frame_locator("//iframe[contains(@src,'bframe')]")
label_obj = captcha_frame.locator("//strong")
prompt = await label_obj.text_content()   # e.g. "Select all images with crosswalks"
```

The solver reads the **task text** from the challenge frame, e.g.:
- "Select all images with **crosswalks**"
- "Select all images with **buses**"
- "Select all images with **traffic lights**"

---

### Step 7: Wait for the Grid to Load

```python
for _ in range(30):
    recaptcha_tiles = await captcha_frame.locator("[class='rc-imageselect-tile']").all()
    if len(recaptcha_tiles) in (9, 16):   # 3x3 or 4x4 grid
        break
    await self.page.wait_for_timeout(1000)
```

The solver waits until the image grid is fully loaded — either **9 tiles** (3×3) or **16 tiles** (4×4, area captcha).

---

### Step 8: Capture the Grid Image (in `detect_tiles()`)

```python
# Capture ONLY the bframe iframe, not the full page
bframe_locator = self.page.locator("//iframe[contains(@src,'bframe')]")
bbox = await bframe_locator.bounding_box()          # Get iframe position
image_bytes = await captcha_frame.locator("body").screenshot()  # Screenshot iframe only
```

The solver captures **only the CAPTCHA iframe content** and records the iframe's position on the page for accurate click coordinates.

---

### Step 9: AI Detection (in `recognizer/components/detector.py`)

```python
response, coordinates = self.detector.detect(prompt, image_bytes, area_captcha=area_captcha)
```

The `Detector` uses **two AI models** to identify which tiles contain the requested object:

**A. YOLO11 Segmentation** (for common objects like cars, buses, bicycles, traffic lights):
```python
outputs = detection_models.yolo_model.predict(image, verbose=False, conf=0.2, iou=0.3)
# For each detected object, check if its class matches the prompt
# Use segmentation masks to determine which grid tiles contain the object
```

**B. CLIP/CLIPSeg** (for harder objects like crosswalks, stairs, mountains, chimneys):
```python
# CLIP: Compares each tile image against text descriptions
probs = logits_per_image.softmax(dim=1)
# CLIPSeg: Segments the image to find areas matching the prompt
```

The detector returns:
- `response`: A list of booleans — `True` for tiles that contain the object
- `coordinates`: The center (x, y) of each matching tile

---

### Step 10: Click the Correct Tiles (in `detect_tiles()` — humanized)

```python
for coord_x, coord_y in click_coords:
    # Human hesitation before click
    await asyncio.sleep(behavior.delay("mouse_hesitation"))

    # Random offset within ±2-8 pixels
    dx, dy = behavior.mouse_offset()
    target_x, target_y = coord_x + dx, coord_y + dy

    # Overshoot correction
    await self.page.mouse.move(target_x + 1-3, target_y + 1-3)
    await asyncio.sleep(behavior.delay("mouse_micro_pause"))
    await self.page.mouse.move(target_x, target_y)

    # Click and wait fresh random delay between tiles
    await self.page.mouse.click(target_x, target_y)
    await asyncio.sleep(behavior.delay("tile_click"))
```

**Humanization:** Every tile click has:
- Small hesitation (0.05-0.6s based on mouse personality)
- Random cursor offset (±2-8 px) staying inside element boundaries
- Tiny overshoot correction (like a real mouse movement)
- Micro pause before click
- **Fresh random delay between each tile** (never reused)

---

### Step 11: Handle Dynamic Challenges

```python
if self.dynamic and not area_captcha:
    while result_clicked:
        await self.page.wait_for_timeout(5000)
        result_clicked = await self.detect_tiles(prompt, area_captcha)
```

If Google shows a **dynamic challenge** ("Click verify once there are none left"), the solver keeps detecting and clicking new tiles until no more matching tiles appear.

---

### Step 12: Submit the Answer (humanized)

```python
# Human pause before pressing verify — as if checking selected tiles (2-6s)
await asyncio.sleep(behavior.delay("verify_pause"))
submit_button = captcha_frame.locator("#recaptcha-verify-button")
await submit_button.click()
```

The solver pauses **2-6 seconds** (profile-adjusted) before clicking the **Verify** button, simulating a user double-checking their selections.

---

### Step 13: Check for Success (in `check_result()`)

```python
# Method 1: Route interceptor captures the token from Google's API response
if "userverify" in request.url and "rresp" not in response_text:
    self.captcha_token = match.group(1)

# Method 2: Read the token from the page
captcha_token = await self.page.evaluate("grecaptcha.getResponse()")
```

The solver checks if a **CAPTCHA token** was obtained via:
1. The **route interceptor** (monitors Google's `userverify` API response)
2. Reading `grecaptcha.getResponse()` from the page

---

### Step 14: Handle Errors & Retry (humanized)

```python
# If "Please try again" error appears
incorrect = captcha_frame.locator("[class='rc-imageselect-incorrect-response']")
if await incorrect.is_visible():
    # Human pause before pressing reload
    await asyncio.sleep(behavior.delay("before_reload"))
    await self.load_captcha(captcha_frame, reset=True)   # Reload grid
    # Wait after reload before solving again
    await asyncio.sleep(behavior.delay("after_reload"))

# If no token after 5 seconds, retry the whole process
return await self.handle_recaptcha()
```

If the answer was wrong, Google shows an error and the solver **reloads the grid** and tries again. Reloads now include a human pause before (1.5-5s) and after (2-5.5s). Retries are randomized **15-25 times** internally (was fixed 15), and **3-10 full attempts** from `captcha_solver.py` (was fixed 3).

---

### Step 15: Verify CAPTCHA Cleared (in `captcha_solver.py`)

```python
if captcha_cleared(page):   # "/sorry/index" not in page.url
    logger.info("YOLOv8 reCAPTCHA solve successful!")
    return True
```

The solver checks if the page URL no longer contains `/sorry/index`. If cleared, the scraper resumes searching.

---

### Step 16: Route Cleanup (in `captcha_solver.py`)

```python
finally:
    await page.unroute_all(behavior="ignoreErrors")
```

After each attempt, the route interceptor is cleaned up to prevent `Route.fetch: Target page, context or browser has been closed` errors.

---

### Visual Flow Summary

```
Google Search → CAPTCHA Detected (/sorry/index)
    ↓
auto_solve_captcha() → HumanBehavior.create() (fresh profile per session)
    ↓
HumanizedAsyncChallenger created (subclasses AsyncChallenger — recognizer untouched)
    ↓
Human pause → Click "I'm not a robot" checkbox
    ↓
Challenge appears → Read prompt text ("Select all images with X")
    ↓
Wait for 3×3 or 4×4 grid to load
    ↓
Screenshot ONLY the bframe iframe
    ↓
YOLO11 detects objects → CLIP/CLIPSeg for hard objects
    ↓
Click matching tiles with human mouse behavior + per-tile random delays
    ↓
Human pause (2-6s) → Click Verify → Check for CAPTCHA token
    ↓
Token obtained? → CAPTCHA cleared → Resume scraping
    ↓
No token? → Human pause → Reload grid → Retry (15-25 × internally, 3-10 × externally)