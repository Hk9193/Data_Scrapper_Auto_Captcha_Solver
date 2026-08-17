import asyncio

import pytest

from human_behavior import _resolve_submit_button


class FakeLocator:
    def __init__(self, *, visible=True, enabled=True, count=1, error=None):
        self.visible = visible
        self.enabled = enabled
        self.count_value = count
        self.error = error
        self.calls = 0

    async def count(self):
        self.calls += 1
        if self.error == "count":
            raise RuntimeError("stale locators")
        return self.count_value

    async def is_visible(self):
        if self.error == "visible":
            raise RuntimeError("detached element")
        return self.visible

    async def is_enabled(self):
        if self.error == "enabled":
            raise RuntimeError("button disabled")
        return self.enabled


class FakeFrame:
    def __init__(self, buttons):
        self._buttons = buttons

    def locator(self, selector):
        return self._buttons[selector]


def test_resolve_submit_button_prefers_verify_then_next():
    verify = FakeLocator()
    next_btn = FakeLocator()
    frame = FakeFrame({"#recaptcha-verify-button": verify, "#recaptcha-next-button": next_btn})

    button, selector = asyncio.run(_resolve_submit_button(frame, timeout=0.2))

    assert button is verify
    assert selector == "#recaptcha-verify-button"


def test_resolve_submit_button_discards_stale_button():
    stale = FakeLocator(error="count")
    next_btn = FakeLocator()
    frame = FakeFrame({"#recaptcha-verify-button": stale, "#recaptcha-next-button": next_btn})

    button, selector = asyncio.run(_resolve_submit_button(frame, timeout=0.2))

    assert button is next_btn
    assert selector == "#recaptcha-next-button"
