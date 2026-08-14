"""
captcha_solver.py — Automated Google reCAPTCHA solving.

Primary: YOLOv8 / YOLO 11 image challenge solver (recognizer / ultralytics).
          Handles the classic Google "Select all images with a <object>"
          (e.g. bus, bicycle, crosswalk) 3x3 / 4x4 grid challenges, including
          the *dynamic* variant that keeps refreshing new tiles after each
          click ("Click verify once there are none left.").
Fallback: Audio challenge + speech-to-text when image solving fails or is blocked.

Humanization: Every CAPTCHA session generates a fresh HumanBehavior profile
              (thinking speed, mouse speed, max YOLO attempts, max retries).
              All timing values are regenerated independently per action.
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from typing import Optional

from playwright.async_api import Page

from human_behavior import HumanBehavior, HumanizedAsyncChallenger
from recovery import BrowserDeadError, is_closed_error

logger = logging.getLogger("scraper")


def captcha_cleared(page: Page) -> bool:
    return "/sorry/index" not in page.url


# Google's HARD rate-limit wall — a plain text page ("Try again later." /
# "Your computer or network may be sending automated queries.") that shows
# NO reCAPTCHA checkbox or image challenge. This is a rate limit, not a
# CAPTCHA, so the YOLO/audio solver MUST NOT be run against it.
#
# This marker set is deliberately a SUBSET: it EXCLUDES the "/sorry/index"
# "unusual traffic" phrasing, which still presents a solvable reCAPTCHA.
_GOOGLE_AUTO_QUERY_MARKERS = (
    "try again later",
    "may be sending automated queries",
    "sending automated queries",
)


async def is_google_automated_query_block(page: Page) -> bool:
    """Return True if *page* is Google's hard automated-queries rate-limit
    wall (a plain-text block with NO solvable CAPTCHA).

    Distinct from a normal "/sorry/index" reCAPTCHA, which the solver can
    legitimately attempt. When this is detected, the caller must stop
    querying, apply a bounded backoff/cooldown, and wait for Google to lift
    the block — never invoke the CAPTCHA solver against it.
    """
    try:
        text = (
            await asyncio.wait_for(page.inner_text("body"), timeout=5)
        ).lower()
    except Exception as exc:
        if is_closed_error(exc):
            raise BrowserDeadError(str(exc)) from exc
        # Transient read failure — treat as NOT the hard block so the normal
        # CAPTCHA path can still make a decision (e.g. network timeout).
        return False
    return any(marker in text for marker in _GOOGLE_AUTO_QUERY_MARKERS)


async def ensure_captcha_checkbox(page: Page) -> bool:
    """
    Ensure the reCAPTCHA checkbox is checked.
    Handles the 'Verification challenge expired' state where the checkbox
    becomes unchecked and needs to be re-clicked.

    Returns True if the checkbox was clicked successfully, False otherwise.
    """
    try:
        anchor_frame = None
        for frame in page.frames:
            if "recaptcha" in frame.url and "anchor" in frame.url:
                anchor_frame = frame
                break

        if not anchor_frame:
            return False

        checkbox = await anchor_frame.query_selector("#recaptcha-anchor")
        if not checkbox:
            return False

        is_checked = await checkbox.get_attribute("aria-checked")
        if is_checked == "false":
            logger.info("reCAPTCHA checkbox is unchecked. Clicking it...")
            await checkbox.click(timeout=8000)
            await asyncio.sleep(2)
            # Check if it triggered a challenge or cleared
            is_checked = await checkbox.get_attribute("aria-checked")
            if is_checked == "true":
                logger.info("reCAPTCHA checkbox successfully checked!")
                return True
            else:
                logger.info("reCAPTCHA checkbox clicked, challenge may have been triggered.")
                return True
        else:
            logger.info("reCAPTCHA checkbox is already checked.")
            return True
    except Exception as e:
        if is_closed_error(e):
            # Never spin on a dead browser — let the caller recreate it.
            raise BrowserDeadError(str(e)) from e
        logger.warning("Error ensuring captcha checkbox: %s", e)
        return False


async def _find_recaptcha_frame(page: Page, frame_kind: str) -> Optional[object]:
    for _ in range(12):
        try:
            for frame in page.frames:
                if "recaptcha" in frame.url and frame_kind in frame.url:
                    return frame
        except Exception as e:
            if is_closed_error(e):
                raise BrowserDeadError(str(e)) from e
            # transient frame error — keep polling
        await asyncio.sleep(0.5)
    return None


def _peek_recaptcha_frame(page: Page, frame_kind: str) -> Optional[object]:
    """Non-blocking, single-scan recaptcha-frame lookup (no polling).

    Used by lightweight detectors that run on every page (e.g. to decide
    whether an active challenge is present) where a 6 s poll on pages that
    contain no reCAPTCHA would be far too slow.
    """
    try:
        for frame in page.frames:
            try:
                if "recaptcha" in frame.url and frame_kind in frame.url:
                    return frame
            except Exception:
                continue
    except Exception as e:
        if is_closed_error(e):
            raise BrowserDeadError(str(e)) from e
    return None


async def _challenge_has_error(bframe) -> bool:
    """Detect 'Please try again' / incorrect-selection messages on the image grid."""
    try:
        error_el = await bframe.query_selector(
            ".rc-imageselect-error-select-more, "
            ".rc-imageselect-error-dynamic-more, "
            ".rc-imageselect-error-select-something, "
            ".rc-imageselect-incorrect-response"
        )
        if error_el:
            is_visible = await error_el.is_visible()
            return is_visible
    except Exception:
        pass
    return False


async def _click_reload_button(page: Page, behavior: HumanBehavior) -> None:
    """Click the circular reload/refresh icon to get a brand-new challenge."""
    bframe = await _find_recaptcha_frame(page, "bframe")
    if not bframe:
        return
    try:
        reload_btn = await bframe.query_selector("#recaptcha-reload-button")
        if reload_btn:
            # Human pause before pressing reload
            await asyncio.sleep(behavior.delay("before_reload"))
            await reload_btn.click()
            # Wait a random duration after reload before solving again
            await asyncio.sleep(behavior.delay("after_reload"))
    except Exception as e:
        if is_closed_error(e):
            raise BrowserDeadError(str(e)) from e
        pass


async def _detect_expired_state(page: Page) -> bool:
    """
    Detect whether the reCAPTCHA challenge has expired.

    Google shows "Verification challenge expired. Check the checkbox again."
    when the challenge has timed out. In this state, the image grid is gone
    (0 tiles) and the checkbox needs to be re-clicked to get a fresh challenge.

    Returns True if the challenge is in an EXPIRED state, False otherwise.
    """
    try:
        bframe = await _find_recaptcha_frame(page, "bframe")
        if not bframe:
            return False

        # Look for the expired-challenge message in the bframe
        expired_el = await bframe.query_selector(
            ".rc-imageselect-desc-no-caption, "
            ".rc-imageselect-desc, "
            "div:has-text('Verification challenge expired'), "
            "div:has-text('Check the checkbox again')"
        )
        if expired_el:
            try:
                text = await expired_el.inner_text()
                if "expired" in text.lower() or "checkbox again" in text.lower():
                    logger.info("EXPIRED CAPTCHA state detected: %s", text.strip())
                    return True
            except Exception:
                pass

        # Also check the anchor frame for the expired state
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
                    # Checkbox unchecked — could be expired or never clicked.
                    # Check if there's an expired message in the bframe.
                    if bframe:
                        expired_msg = await bframe.query_selector(
                            "div:has-text('expired'), "
                            "div:has-text('checkbox again')"
                        )
                        if expired_msg:
                            logger.info(
                                "EXPIRED CAPTCHA state detected (checkbox unchecked + expired message)."
                            )
                            return True
    except Exception as e:
        if is_closed_error(e):
            raise BrowserDeadError(str(e)) from e
        logger.warning("Error detecting expired CAPTCHA state: %s", e)

    return False


async def _count_challenge_images(page: Page) -> int:
    """
    Count the number of image tiles in the active reCAPTCHA challenge.

    Returns the number of visible `.rc-imageselect-tile` elements in the
    bframe. A valid challenge has either 9 (3x3) or 16 (4x4) images.
    Returns 0 if no challenge is active or the frame is not found.
    """
    try:
        bframe = await _find_recaptcha_frame(page, "bframe")
        if not bframe:
            return 0

        tiles = await bframe.query_selector_all(".rc-imageselect-tile")
        if not tiles:
            return 0

        # Count only visible tiles
        visible_count = 0
        for tile in tiles:
            try:
                if await tile.is_visible():
                    visible_count += 1
            except Exception:
                pass
        return visible_count
    except Exception as e:
        if is_closed_error(e):
            raise BrowserDeadError(str(e)) from e
        logger.warning("Error counting challenge images: %s", e)
        return 0


async def active_image_challenge_present(page: Page) -> bool:
    """
    Return True if an ACTIVE (non-expired) image CAPTCHA challenge is
    currently displayed — e.g. "Select all images with crosswalks" with a
    3x3/4x4 grid, or the "Please select all matching images." state.

    This is used to AVOID refreshing/reinitializing a challenge that is
    already presented: we must not re-click the checkbox or reload the grid,
    because that would destroy the very challenge a human is meant to solve.

    It is NOT the expired state ("Verification challenge expired. Check the
    checkbox again.") — that state intentionally returns False so the normal
    expired-recovery path can reinitialize it.

    Note: this uses a non-blocking frame peek so it is cheap to call on every
    page (e.g. inside _ensure_no_captcha) with no reCAPTCHA present.
    """
    try:
        bframe = _peek_recaptcha_frame(page, "bframe")
        if bframe is None:
            return False

        # A live 3x3 / 4x4 grid means an active challenge is up. The grid
        # counter finds the (now-present) frame on its first pass.
        image_count = await _count_challenge_images(page)

        # 1) A live 3x3 / 4x4 grid means an active challenge is up.
        if image_count in (9, 16):
            return True

        # 2) The challenge prompt/descriptor is the strongest signal for an
        #    active grid. Active = "Select all images with crosswalks" /
        #    "Please select all matching images." — NOT the expired message.
        prompt = await bframe.query_selector(
            ".rc-imageselect-desc-no-caption, "
            ".rc-imageselect-desc, "
            ".rc-imageselect-instructions, "
            "div:has-text('Please select all matching images')"
        )
        if prompt:
            try:
                text = (await prompt.inner_text() or "").strip().lower()
            except Exception:
                text = ""
            if (
                text
                and "expired" not in text
                and "checkbox again" not in text
                and (
                    "select all" in text
                    or "matching images" in text
                    or image_count > 0
                )
            ):
                logger.info("Active image challenge prompt detected: %s", text)
                return True
    except Exception as e:
        if is_closed_error(e):
            raise BrowserDeadError(str(e)) from e
        logger.warning("Error detecting active image challenge: %s", e)

    return False


async def _wait_for_fresh_challenge(
    page: Page,
    behavior: HumanBehavior,
    timeout: float = 30.0,
) -> bool:
    """
    Reinitialize the CAPTCHA checkbox and wait for a fresh image challenge.

    Handles the EXPIRED state by:
      1. Cleaning up any leftover routes from previous solver attempts.
      2. Re-clicking the reCAPTCHA checkbox to trigger a fresh challenge.
      3. Waiting (up to `timeout` seconds) for a challenge with 9 or 16 images.

    Returns True if a fresh challenge with 9/16 images is detected,
    False if the timeout was reached without a valid challenge.
    """
    logger.info("Attempting to recover from expired CAPTCHA state...")

    # Clean up any leftover routes from previous solver attempts
    try:
        await page.unroute_all(behavior="ignoreErrors")
    except Exception:
        pass

    # Re-click the checkbox to trigger a fresh challenge
    checkbox_ok = await ensure_captcha_checkbox(page)
    if not checkbox_ok:
        logger.warning("Could not re-click the reCAPTCHA checkbox.")

    # Wait for a fresh challenge with 9 or 16 images
    elapsed = 0.0
    poll_interval = 1.0
    while elapsed < timeout:
        # CHECK IF CAPTCHA WAS CLEARED ENTIRELY BEFORE POLLING
        if captcha_cleared(page):
            logger.info("CAPTCHA cleared during fresh-challenge wait.")
            return True

        image_count = await _count_challenge_images(page)
        if image_count in (9, 16):
            logger.info(
                "Fresh challenge detected with %d images. Ready for YOLO solver.",
                image_count,
            )
            return True

        # If image_count is 0, the challenge has disappeared/dissolved.
        # Do NOT keep polling — break early to avoid unnecessary wait.
        if image_count == 0:
            logger.info(
                "Challenge disappeared (0 images) during fresh-challenge wait. "
                "Breaking early to avoid unnecessary wait."
            )
            break

        # If still expired, try re-clicking the checkbox again
        expired = await _detect_expired_state(page)
        if expired:
            logger.info("Still in expired state. Re-clicking checkbox...")
            await ensure_captcha_checkbox(page)

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    logger.warning(
        "Timed out waiting for fresh CAPTCHA challenge after %.1f seconds.",
        timeout,
    )
    return False


async def solve_recaptcha_yolo(
    page: Page,
    behavior: HumanBehavior,
    max_attempts: Optional[int] = None,
) -> bool:
    """
    Solve reCAPTCHA image challenges with YOLOv8 (recognizer AsyncChallenger).

    Retries up to *max_attempts* times because Google sometimes keeps issuing
    new image grids ("Please try again.") even after a valid selection —
    a single pass through the solver is not always enough to clear it.

    Before calling the recognizer, this function:
      1. Detects the EXPIRED state ("Verification challenge expired" /
         "Check the checkbox again") and recovers by re-clicking the checkbox
         and waiting for a fresh challenge.
      2. Verifies the image challenge actually contains 9 or 16 images.
         If 0 images are detected, YOLO is NOT called and no retry loop
         is entered — preventing the "Images amount must equal 9 or 16. Is: 0"
         error loop.

    max_attempts defaults to behavior.max_yolo_attempts (random 3-10 per session).
    """
    if max_attempts is None:
        max_attempts = behavior.max_yolo_attempts

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(
                "Attempting YOLOv8 image reCAPTCHA solve (recognizer) — attempt %d/%d...",
                attempt,
                max_attempts,
            )

            # Human pause before clicking the checkbox
            await asyncio.sleep(behavior.delay("before_checkbox"))

            # --- An ACTIVE image challenge (3x3/4x4 grid) is exactly what the
            # automated solver is here to resolve in unattended 24/7 mode, so we
            # PROCEED to solve it (do NOT skip). The subsequent 9/16-image count
            # and expired-state checks make sure we only call YOLO on a real,
            # solvable grid and never loop on a zero-image / expired challenge.
            # (The old behaviour of returning False here disabled auto-solving on
            # every real CAPTCHA and guaranteed a timeout when no human watched.)
            if await active_image_challenge_present(page):
                logger.info(
                    "ACTIVE IMAGE CAPTCHA DETECTED (grid present) - proceeding "
                    "with automated solve."
                )

            # --- Detect EXPIRED state before calling YOLO ---
            if await _detect_expired_state(page):
                logger.warning(
                    "CAPTCHA challenge is EXPIRED. Recovering before YOLO solve..."
                )
                # Clean up any leftover routes from previous attempts
                try:
                    await page.unroute_all(behavior="ignoreErrors")
                except Exception:
                    pass

                # Reinitialize the checkbox and wait for a fresh challenge
                recovered = await _wait_for_fresh_challenge(
                    page, behavior, timeout=30.0
                )
                if not recovered:
                    logger.warning(
                        "Could not recover from expired CAPTCHA state. "
                        "Returning False so manual fallback can take over."
                    )
                    return False

                # If the CAPTCHA was cleared during recovery, we're done
                if captcha_cleared(page):
                    logger.info("CAPTCHA cleared during expired-state recovery!")
                    return True

            # --- Verify image challenge has 9 or 16 images before YOLO ---
            image_count = await _count_challenge_images(page)
            if image_count == 0:
                logger.warning(
                    "No active image challenge detected (0 images). "
                    "Skipping YOLO solver to avoid the 'Images amount must equal "
                    "9 or 16. Is: 0' error loop."
                )
                # Try to recover by re-clicking the checkbox and waiting
                recovered = await _wait_for_fresh_challenge(
                    page, behavior, timeout=30.0
                )
                if not recovered:
                    logger.warning(
                        "Could not obtain a fresh challenge with 9/16 images. "
                        "Returning False so manual fallback can take over."
                    )
                    return False

                if captcha_cleared(page):
                    logger.info("CAPTCHA cleared during fresh-challenge recovery!")
                    return True

                # Re-count after recovery
                image_count = await _count_challenge_images(page)
                if image_count not in (9, 16):
                    logger.warning(
                        "Fresh challenge still has %d images (expected 9 or 16). "
                        "Skipping YOLO solver.",
                        image_count,
                    )
                    return False

            logger.info(
                "Image challenge verified: %d images detected. Starting YOLO solver.",
                image_count,
            )

            # RE-VERIFY challenge state immediately before calling the recognizer.
            # Google can refresh the grid between the count check and now.
            if not await active_image_challenge_present(page):
                logger.warning(
                    "Challenge disappeared before YOLO solve (attempt %d). "
                    "Re-initializing...",
                    attempt,
                )
                # Recycle the route handlers and retry the loop iteration
                try:
                    await page.unroute_all(behavior="ignoreErrors")
                except Exception:
                    pass
                continue

            challenger = HumanizedAsyncChallenger(
                page,
                human_behavior=behavior,
            )
            await challenger.solve_recaptcha()

            # Human pause after successful recognition before checking result
            await asyncio.sleep(behavior.delay("after_success"))

            # Check if CAPTCHA was successfully solved AFTER the human pause.
            # The pause ensures the page has time to transition to the post-solve state.
            if captcha_cleared(page):
                logger.info("YOLOv8 reCAPTCHA solve successful!")
                return True

            # The solver ran but the CAPTCHA is still active.
            # Distinguish between: (a) solver genuinely failed, vs (b) page just
            # needs a moment to update. Log and retry rather than treating this
            # as a permanent failure on this attempt.
            logger.warning(
                "YOLOv8 solver attempt %d/%d finished but CAPTCHA "
                "page is still active — will retry (if attempts remain).",
                attempt,
                max_attempts,
            )
        except Exception as err:
            if is_closed_error(err) or isinstance(err, BrowserDeadError):
                raise BrowserDeadError(str(err)) from err
            logger.warning(
                "YOLOv8 reCAPTCHA solve error on attempt %d/%d: %s",
                attempt,
                max_attempts,
                err,
            )
        finally:
            # Clean up the route handler set up by AsyncChallenger.
            # Prevents "Route.fetch: Target page, context or browser has been closed"
            # from leaking into subsequent attempts / page lifecycle.
            try:
                await page.unroute_all(behavior="ignoreErrors")
            except Exception:
                pass

        if attempt < max_attempts:
            # Get a fresh grid before trying again — avoids getting stuck
            # re-analysing the exact same (already-wrong) tiles.
            await _click_reload_button(page, behavior)

    return False


async def solve_recaptcha_audio(
    page: Page,
    behavior: HumanBehavior,
    max_attempts: Optional[int] = None,
) -> bool:
    """Fallback: solve reCAPTCHA via audio challenge + Google Speech Recognition."""
    if max_attempts is None:
        max_attempts = 2  # audio fallback stays at 2 attempts

    try:
        import static_ffmpeg

        static_ffmpeg.add_paths()
    except Exception:
        pass

    try:
        import speech_recognition as sr
        from pydub import AudioSegment
    except ImportError:
        logger.warning(
            "SpeechRecognition/pydub not installed. Install with: "
            "pip install SpeechRecognition pydub static-ffmpeg"
        )
        return False

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(
                "Attempting audio reCAPTCHA solve (fallback) — attempt %d/%d...",
                attempt,
                max_attempts,
            )

            anchor_frame = await _find_recaptcha_frame(page, "anchor")
            if anchor_frame:
                checkbox = await anchor_frame.query_selector("#recaptcha-anchor")
                if checkbox:
                    logger.info("Clicking 'I'm not a robot' checkbox...")
                    # Human pause before clicking checkbox
                    await asyncio.sleep(behavior.delay("before_checkbox"))
                    await checkbox.click(timeout=8000)
                    await asyncio.sleep(behavior.delay("after_challenge_load"))

            if captcha_cleared(page):
                logger.info("reCAPTCHA solved by checkbox click!")
                return True

            bframe = await _find_recaptcha_frame(page, "bframe")
            if not bframe:
                logger.warning("Challenge frame (bframe) not found after checkbox click.")
                return False

            audio_button = await bframe.wait_for_selector(
                "#recaptcha-audio-button", timeout=5000
            )
            if audio_button:
                logger.info("Clicking Audio Challenge button...")
                await audio_button.click()
                await asyncio.sleep(behavior.delay("audio_wait"))

            dos_element = await bframe.query_selector(
                '.rc-dossafety-header, .rc-audiochallenge-error-message, div:has-text("Try again later")'
            )
            if dos_element:
                logger.warning("\n" + "=" * 70)
                logger.warning("GOOGLE IP BLOCK DETECTED: 'Try again later'")
                logger.warning(
                    "Google has temporarily disabled audio CAPTCHAs for this IP."
                )
                logger.warning(
                    "FIX: Switch VPN or use mobile hotspot to get a fresh IP, "
                    "or rely on the YOLO image solver."
                )
                logger.warning("=" * 70 + "\n")
                return False

            audio_link = None
            for selector in [
                ".rc-audiochallenge-tdownload-link",
                'a[href*="payload"]',
                'a[href*="audio"]',
            ]:
                try:
                    audio_link = await bframe.wait_for_selector(selector, timeout=3000)
                    if audio_link:
                        break
                except Exception:
                    pass

            if not audio_link:
                logger.warning("Audio download link not found.")
                return False

            src = await audio_link.get_attribute("href")
            if not src:
                return False

            logger.info("Downloading audio challenge...")
            response = await page.request.get(src)
            audio_bytes = await response.body()

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                tmp_mp3.write(audio_bytes)
                mp3_path = tmp_mp3.name

            wav_path = mp3_path.replace(".mp3", ".wav")

            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                digits = recognizer.recognize_google(audio_data)
                logger.info("Transcribed CAPTCHA digits: %s", digits)

            input_box = await bframe.wait_for_selector("#audio-response", timeout=4000)
            if input_box:
                await input_box.fill(digits)
                await asyncio.sleep(behavior.delay("audio_input"))
                verify_btn = await bframe.wait_for_selector(
                    "#recaptcha-verify-button", timeout=4000
                )
                if verify_btn:
                    # Human pause before pressing verify
                    await asyncio.sleep(behavior.delay("verify_pause"))
                    await verify_btn.click()
                    await asyncio.sleep(behavior.delay("audio_verify"))

            try:
                os.remove(mp3_path)
                os.remove(wav_path)
            except Exception:
                pass

            if captcha_cleared(page):
                logger.info("Audio reCAPTCHA solve successful!")
                return True

            logger.warning(
                "Audio solve attempt %d/%d did not clear the CAPTCHA.",
                attempt,
                max_attempts,
            )

        except Exception as err:
            if is_closed_error(err) or isinstance(err, BrowserDeadError):
                raise BrowserDeadError(str(err)) from err
            logger.warning(
                "Audio CAPTCHA solve error on attempt %d/%d: %s",
                attempt,
                max_attempts,
                err,
            )

        if attempt < max_attempts:
            await asyncio.sleep(behavior.delay("audio_wait"))

    return False


async def auto_solve_captcha(page: Page, method: str = "yolo_then_audio") -> bool:
    """
    Solve Google reCAPTCHA on the current page.

    method:
      - "yolo"            — YOLOv8 image solver only
      - "audio"           — audio challenge only
      - "yolo_then_audio" — try YOLO first, then audio fallback (default)

    A fresh HumanBehavior profile is generated for every CAPTCHA session.
    """
    # Generate a fresh HumanBehavior for this CAPTCHA session
    behavior = HumanBehavior.create()
    behavior.log_session_info()

    if method in ("yolo", "yolo_then_audio"):
        if await solve_recaptcha_yolo(page, behavior):
            return True

    if method in ("audio", "yolo_then_audio"):
        return await solve_recaptcha_audio(page, behavior)

    return False