"""
captcha_solver.py — Automated Google reCAPTCHA solving.

Primary: YOLOv8 image challenge solver (recognizer / ultralytics).
          Handles the classic Google "Select all images with a <object>"
          (e.g. bus, bicycle, crosswalk) 3x3 / 4x4 grid challenges, including
          the *dynamic* variant that keeps refreshing new tiles after each
          click ("Click verify once there are none left.").
Fallback: Audio challenge + speech-to-text when image solving fails or is blocked.
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import tempfile
from typing import Optional

from playwright.async_api import Page

logger = logging.getLogger("scraper")

# How many full solve attempts to give the YOLO solver before giving up on it.
# Google occasionally re-serves a fresh grid ("Please try again") even after a
# technically-correct selection, so a single attempt is not always enough.
YOLO_MAX_ATTEMPTS = 3
AUDIO_MAX_ATTEMPTS = 2


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


async def _click_reload_button(page: Page) -> None:
    """Click the circular reload/refresh icon to get a brand-new challenge."""
    bframe = await _find_recaptcha_frame(page, "bframe")
    if not bframe:
        return
    try:
        reload_btn = await bframe.query_selector("#recaptcha-reload-button")
        if reload_btn:
            await reload_btn.click()
            await asyncio.sleep(1.5)
    except Exception:
        pass


async def solve_recaptcha_yolo(page: Page, max_attempts: int = YOLO_MAX_ATTEMPTS) -> bool:
    """
    Solve reCAPTCHA image challenges with YOLOv8 (recognizer AsyncChallenger).

    Retries up to *max_attempts* times because Google sometimes keeps issuing
    new image grids ("Please try again.") even after a valid selection —
    a single pass through the solver is not always enough to clear it.
    """
    try:
        # pyrefly: ignore [missing-import]
        from recognizer.agents.playwright import AsyncChallenger
    except ImportError:
        logger.warning(
            "recognizer is not installed. Install with: pip install recognizer"
        )
        return False

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(
                "Attempting YOLOv8 image reCAPTCHA solve (recognizer) — attempt %d/%d...",
                attempt,
                max_attempts,
            )
            challenger = AsyncChallenger(
                page,
                click_timeout=1500,
                optimize_click_order=True,
            )
            await challenger.solve_recaptcha()
            await asyncio.sleep(2.5)

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

        if attempt < max_attempts:
            # Get a fresh grid before trying again — avoids getting stuck
            # re-analysing the exact same (already-wrong) tiles.
            await _click_reload_button(page)
            await asyncio.sleep(random.uniform(1.0, 2.0))

    return False



async def solve_recaptcha_audio(page: Page, max_attempts: int = AUDIO_MAX_ATTEMPTS) -> bool:
    """Fallback: solve reCAPTCHA via audio challenge + Google Speech Recognition."""
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
                    await checkbox.click()
                    await asyncio.sleep(2.5)

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
                await asyncio.sleep(2)

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
                await asyncio.sleep(1)
                verify_btn = await bframe.wait_for_selector(
                    "#recaptcha-verify-button", timeout=4000
                )
                if verify_btn:
                    await verify_btn.click()
                    await asyncio.sleep(3)

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
            await asyncio.sleep(random.uniform(1.5, 3.0))

    return False



async def auto_solve_captcha(page: Page, method: str = "yolo_then_audio") -> bool:
    """
    Solve Google reCAPTCHA on the current page.

    method:
      - "yolo"            — YOLOv8 image solver only
      - "audio"           — audio challenge only
      - "yolo_then_audio" — try YOLO first, then audio fallback (default)
    """
    if method in ("yolo", "yolo_then_audio"):
        if await solve_recaptcha_yolo(page):
            return True

    if method in ("audio", "yolo_then_audio"):
        return await solve_recaptcha_audio(page)

    return False
