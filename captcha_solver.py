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

logger = logging.getLogger("scraper")


def captcha_cleared(page: Page) -> bool:
    return "/sorry/index" not in page.url


async def _find_recaptcha_frame(page: Page, frame_kind: str) -> Optional[object]:
    for _ in range(12):
        for frame in page.frames:
            if "recaptcha" in frame.url and frame_kind in frame.url:
                return frame
        await asyncio.sleep(0.5)
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
    except Exception:
        pass


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

            challenger = HumanizedAsyncChallenger(
                page,
                human_behavior=behavior,
            )
            await challenger.solve_recaptcha()

            # Human pause after successful recognition before checking result
            await asyncio.sleep(behavior.delay("after_success"))

            if captcha_cleared(page):
                logger.info("YOLOv8 reCAPTCHA solve successful!")
                return True

            logger.warning(
                "YOLOv8 solver attempt %d/%d finished but CAPTCHA page is still active.",
                attempt,
                max_attempts,
            )
        except Exception as err:
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
                    await checkbox.click()
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