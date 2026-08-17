"""
human_behavior.py — Human-like behavior profiles for CAPTCHA solving sessions.

This module provides:
  - HumanBehavior: session-level configuration with behavior profiles
  - HumanizedAsyncChallenger: wrapper around recognizer's AsyncChallenger
    that adds human-like per-tile delays and mouse behavior

The recognizer library, YOLO model, and detection pipeline are NOT modified.
This module only wraps behavior around the existing recognizer.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

logger = logging.getLogger("scraper")

try:
    from recognizer.agents.playwright import AsyncChallenger
except ImportError:
    AsyncChallenger = None  # type: ignore


class _AsyncChallengerBase:
    """Fallback base class when recognizer is not installed."""
    pass


class ThinkingProfile(Enum):
    """How quickly a human thinks/reacts during a CAPTCHA session."""
    FAST = "Fast"
    NORMAL = "Normal"
    CAREFUL = "Careful"


class MousePersonality(Enum):
    """How quickly a human moves the mouse during a CAPTCHA session."""
    FAST = "Fast"
    MEDIUM = "Medium"
    SLOW = "Slow"


@dataclass
class HumanBehavior:
    """
    Session-level human behavior configuration.

    Generated once per CAPTCHA session. All timing values are
    regenerated independently on every call to delay().
    """

    thinking_profile: ThinkingProfile
    mouse_personality: MousePersonality
    max_yolo_attempts: int
    max_retries: int

    _timing_ranges: dict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._timing_ranges = self._build_timing_ranges()

    @classmethod
    def create(cls) -> "HumanBehavior":
        """Create a new random HumanBehavior for a CAPTCHA session."""
        thinking = random.choice(list(ThinkingProfile))
        mouse = random.choice(list(MousePersonality))
        max_yolo = random.randint(2, 4)
        max_retries = random.randint(3, 6)
        return cls(
            thinking_profile=thinking,
            mouse_personality=mouse,
            max_yolo_attempts=max_yolo,
            max_retries=max_retries,
        )

    def _build_timing_ranges(self) -> dict:
        """Build timing ranges based on thinking profile and mouse personality."""
        ranges = {
            "before_checkbox": (0.7, 2.8),
            "before_verify": (2.1, 6.4),
            "after_challenge_load": (1.5, 5.0),
            "after_success": (1.8, 4.2),
            "after_reload": (2.0, 5.5),
            "before_reload": (1.5, 5.0),
            "tile_click": (0.8, 3.0),
            "mouse_hesitation": (0.1, 0.4),
            "mouse_micro_pause": (0.05, 0.2),
            "verify_pause": (0.35, 1.2),
            "frame_poll": (0.3, 0.8),
            "audio_wait": (1.5, 3.5),
            "audio_input": (0.5, 1.5),
            "audio_verify": (2.0, 4.0),
        }

        if self.thinking_profile == ThinkingProfile.FAST:
            ranges["before_checkbox"] = (0.5, 1.5)
            ranges["before_verify"] = (1.5, 3.5)
            ranges["after_challenge_load"] = (1.0, 2.5)
            ranges["after_success"] = (1.2, 2.5)
            ranges["after_reload"] = (1.5, 3.0)
            ranges["before_reload"] = (1.0, 2.5)
            ranges["tile_click"] = (0.5, 1.5)
            ranges["verify_pause"] = (0.25, 0.9)
            ranges["frame_poll"] = (0.2, 0.5)
            ranges["audio_wait"] = (1.0, 2.0)
            ranges["audio_input"] = (0.3, 0.8)
            ranges["audio_verify"] = (1.5, 3.0)
        elif self.thinking_profile == ThinkingProfile.CAREFUL:
            ranges["before_checkbox"] = (1.0, 3.5)
            ranges["before_verify"] = (3.0, 7.0)
            ranges["after_challenge_load"] = (2.0, 6.0)
            ranges["after_success"] = (2.5, 5.0)
            ranges["after_reload"] = (2.5, 6.0)
            ranges["before_reload"] = (2.0, 5.5)
            ranges["tile_click"] = (1.0, 3.5)
            ranges["verify_pause"] = (0.5, 1.1)
            ranges["frame_poll"] = (0.4, 1.0)
            ranges["audio_wait"] = (2.0, 4.0)
            ranges["audio_input"] = (0.8, 2.0)
            ranges["audio_verify"] = (2.5, 5.0)

        if self.mouse_personality == MousePersonality.FAST:
            ranges["mouse_hesitation"] = (0.05, 0.2)
            ranges["mouse_micro_pause"] = (0.02, 0.1)
        elif self.mouse_personality == MousePersonality.SLOW:
            ranges["mouse_hesitation"] = (0.2, 0.6)
            ranges["mouse_micro_pause"] = (0.1, 0.3)

        return ranges

    def delay(self, key: str) -> float:
        """Generate a fresh random delay for the given timing key."""
        low, high = self._timing_ranges[key]
        return random.uniform(low, high)

    def click_timeout_ms(self) -> int:
        """Get a random click_timeout value (ms) for AsyncChallenger."""
        low, high = self._timing_ranges["tile_click"]
        return int(random.uniform(low, high) * 1000)

    def mouse_offset(self) -> Tuple[int, int]:
        """Generate a random mouse offset within ±2-8 pixels."""
        offset_x = random.choice([-1, 1]) * random.randint(2, 8)
        offset_y = random.choice([-1, 1]) * random.randint(2, 8)
        return offset_x, offset_y

    def log_session_info(self) -> None:
        """Log the session configuration for debugging."""
        logger.info("=" * 50)
        logger.info("CAPTCHA Session Started")
        logger.info(f"Behaviour Profile: {self.thinking_profile.value}")
        logger.info(f"Maximum YOLO Attempts: {self.max_yolo_attempts}")
        logger.info(f"Maximum Retries: {self.max_retries}")
        logger.info(f"Mouse Speed: {self.mouse_personality.value}")
        logger.info("=" * 50)


async def _resolve_submit_button(captcha_frame, timeout: float = 5.0):
    """Resolve the current Google submit button without holding stale DOM references.

    Google swaps the challenge UI after every selection phase; the stale element from
    a previous DOM snapshot can remain visible in the locator tree while the actual
    button is replaced. We therefore re-query the bframe on each poll cycle and only
    click a button that is both visible and enabled.
    """
    selectors = ("#recaptcha-verify-button", "#recaptcha-next-button")
    deadline = time.monotonic() + timeout
    last_error = None

    while time.monotonic() < deadline:
        for selector in selectors:
            try:
                button = captcha_frame.locator(selector)
                count = await button.count()
                if count <= 0:
                    continue
                visible = await button.is_visible()
                enabled = await button.is_enabled()
                if visible and enabled:
                    logger.info(
                        "CAPTCHA state=challenge-active | button_state=%s visible=%s enabled=%s | action=click_submit | result=ready",
                        selector,
                        visible,
                        enabled,
                    )
                    return button, selector
            except Exception as exc:  # pragma: no cover - defensive stale handle reset
                last_error = exc
                continue
        await asyncio.sleep(0.12)

    if last_error is not None:
        logger.warning(
            "CAPTCHA state=challenge-transition | button_state=unresolved | action=click_submit | result=stale_or_detached (%s)",
            last_error,
        )
    else:
        logger.warning(
            "CAPTCHA state=challenge-transition | button_state=unresolved | action=click_submit | result=timeout",
        )
    return None, None


class HumanizedAsyncChallenger(
    AsyncChallenger if AsyncChallenger is not None else _AsyncChallengerBase
):
    """
    Wrapper around recognizer's AsyncChallenger that adds human-like
    per-tile delays and mouse behavior.

    This does NOT modify the recognizer source code. It subclasses
    AsyncChallenger and overrides detect_tiles() to add human-like
    clicking behavior.
    """

    def __init__(
        self,
        page,
        human_behavior: HumanBehavior,
        **kwargs,
    ) -> None:
        if AsyncChallenger is None:
            raise ImportError(
                "recognizer is not installed. Install with: pip install recognizer"
            )

        # Pass retry_times from human_behavior if not explicitly provided
        if "retry_times" not in kwargs:
            kwargs["retry_times"] = human_behavior.max_retries
        # Disable the fixed click_timeout; we handle per-tile delays ourselves
        kwargs["click_timeout"] = None

        super().__init__(page, **kwargs)
        self.human_behavior = human_behavior

    async def load_captcha(
        self,
        captcha_frame=None,
        reset: Optional[bool] = False,
    ):
        """
        Override of AsyncChallenger.load_captcha() that adds a human pause
        before clicking the reload button.
        """
        # Retrying
        self.retried += 1
        if self.retried >= self.retry_times:
            raise RecursionError(f"Exceeded maximum retry times of {self.retry_times}")

        if not await self.check_captcha_visible():
            if captcha_token := await self.check_result():
                return captcha_token
            elif not await self.click_checkbox():
                raise TimeoutError("Invisible reCaptcha Timed Out.")

        assert await self.check_captcha_visible(), TimeoutError(
            "[ERROR] reCaptcha Challenge is not visible."
        )

        # Clicking Reload Button with human pause
        if reset:
            assert captcha_frame is not None
            try:
                reload_button = captcha_frame.locator("#recaptcha-reload-button")
                # Human pause before pressing reload
                await asyncio.sleep(self.human_behavior.delay("before_reload"))
                await reload_button.click()
                # Wait after reload before solving again
                await asyncio.sleep(self.human_behavior.delay("after_reload"))
            except Exception:
                return await self.load_captcha()

            # Resetting Values
            self.dynamic = False
            self.captcha_token = ""

        return True

    async def handle_recaptcha(self):
        """
        Override of AsyncChallenger.handle_recaptcha() that adds a human
        pause before pressing the verify button.
        """
        if isinstance(loaded_captcha := await self.load_captcha(), str):
            return loaded_captcha

        # Getting the Captcha Frame
        captcha_frame = self.page.frame_locator("//iframe[contains(@src,'bframe')]")
        label_obj = captcha_frame.locator("//strong")
        if not (prompt := await label_obj.text_content()):
            raise ValueError("reCaptcha Task Text did not load.")

        # Checking if Captcha Loaded Properly
        for _ in range(30):
            # Getting Recaptcha Tiles
            recaptcha_tiles = await captcha_frame.locator(
                "[class='rc-imageselect-tile']"
            ).all()
            tiles_visibility = [await tile.is_visible() for tile in recaptcha_tiles]
            if len(recaptcha_tiles) in (9, 16) and len(tiles_visibility) in (9, 16):
                break

            await self.page.wait_for_timeout(1000)
        else:
            await self.load_captcha(captcha_frame, reset=True)
            await self.page.wait_for_timeout(2000)
            return await self.handle_recaptcha()

        # Detecting Images and Clicking right Coordinates
        area_captcha = len(recaptcha_tiles) == 16
        result_clicked = await self.detect_tiles(prompt, area_captcha)

        if self.dynamic and not area_captcha:
            while result_clicked:
                await self.page.wait_for_timeout(1800)
                result_clicked = await self.detect_tiles(prompt, area_captcha)
        elif not result_clicked:
            await self.load_captcha(captcha_frame, reset=True)
            await self.page.wait_for_timeout(2000)
            return await self.handle_recaptcha()

        # Human pause before pressing verify — as if checking selected tiles
        await asyncio.sleep(self.human_behavior.delay("verify_pause"))

        # Re-read the current challenge state before interacting. Google replaces
        # the bframe DOM after tile selection, so any saved locator may be stale.
        submit_button, submit_selector = await _resolve_submit_button(captcha_frame, timeout=0.8)
        if submit_button is None:
            logger.warning(
                "CAPTCHA state=post-selection | button_state=none_ready | action=submit_click | result=stop_for_manual_fallback"
            )
            raise TimeoutError("reCAPTCHA submit button changed or became stale; deferring to manual fallback.")

        # Submit challenge
        try:
            logger.info(
                "CAPTCHA state=post-selection | button_state=%s | action=click_submit | result=pending",
                submit_selector,
            )
            await submit_button.click(timeout=5000)
            logger.info(
                "CAPTCHA state=post-selection | button_state=%s | action=click_submit | result=clicked",
                submit_selector,
            )
        except Exception:
            logger.warning(
                "CAPTCHA state=post-selection | button_state=%s | action=click_submit | result=stale_or_intercepted",
                submit_selector,
            )
            await self.load_captcha(captcha_frame, reset=True)
            await self.page.wait_for_timeout(2000)
            return await self.handle_recaptcha()

        # Waiting for captcha_token for 5 seconds
        for _ in range(5):
            if captcha_token := await self.check_result():
                return captcha_token

            await self.page.wait_for_timeout(1000)

        # Check if error occurred whilst solving
        incorrect = captcha_frame.locator(
            "[class='rc-imageselect-incorrect-response']"
        )
        errors = captcha_frame.locator("[class *= 'rc-imageselect-error']")
        if await incorrect.is_visible() or any(
            [await error.is_visible() for error in await errors.all()]
        ):
            await self.load_captcha(captcha_frame, reset=True)

        # Retrying
        await self.page.wait_for_timeout(2000)
        return await self.handle_recaptcha()

    async def detect_tiles(self, prompt: str, area_captcha: bool) -> bool:
        """
        Detect and click tiles with human-like per-tile delays and mouse offsets.

        Replicates the parent's detection logic but adds:
          - Small hesitation before each click
          - Random offset (±2-8 pixels) within element boundaries
          - Mouse move with slight overshoot correction
          - Micro pause before click
          - Fresh random delay between tile clicks
        """
        captcha_frame = self.page.frame_locator("//iframe[contains(@src,'bframe')]")
        is_iframe_capture = False
        offset_x, offset_y = 0, 0
        try:
            bframe_locator = self.page.locator("//iframe[contains(@src,'bframe')]")
            bbox = await bframe_locator.bounding_box()
            if not bbox:
                return False
            offset_x, offset_y = int(bbox["x"]), int(bbox["y"])
            image_bytes = await captcha_frame.locator("body").screenshot()
            is_iframe_capture = True
        except Exception:
            client = await self.page.context.new_cdp_session(self.page)
            image = await client.send("Page.captureScreenshot")
            image_bytes = base64.b64decode(image["data"].encode())
            offset_x, offset_y = 0, 0

        response, coordinates = self.detector.detect(
            prompt, image_bytes, area_captcha=area_captcha
        )

        if not any(response):
            return False

        if is_iframe_capture:
            click_coords = [(x + offset_x, y + offset_y) for x, y in coordinates]
        else:
            click_coords = await self.adjust_coordinates(coordinates, image_bytes)

        for coord_x, coord_y in click_coords:
            # Small hesitation before click
            await asyncio.sleep(self.human_behavior.delay("mouse_hesitation"))

            # Random offset within ±2-8 pixels
            dx, dy = self.human_behavior.mouse_offset()
            target_x = coord_x + dx
            target_y = coord_y + dy

            # Move mouse with slight overshoot correction
            overshoot_x = target_x + random.randint(1, 3)
            overshoot_y = target_y + random.randint(1, 3)
            await self.page.mouse.move(overshoot_x, overshoot_y)
            await asyncio.sleep(self.human_behavior.delay("mouse_micro_pause"))
            await self.page.mouse.move(target_x, target_y)

            # Micro pause before click
            await asyncio.sleep(self.human_behavior.delay("mouse_micro_pause"))

            # Click
            await self.page.mouse.click(target_x, target_y)

            # Fresh random delay between tile clicks
            await asyncio.sleep(self.human_behavior.delay("tile_click"))

        return True