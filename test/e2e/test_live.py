from typing import Tuple, Callable
from pytest import mark
from playwright.sync_api import Page, expect


def test_live_indicator(
    page: Page,
    set_live: Tuple[Callable, str],
):
    # explicitly defining tuple objects for clarity
    replace_live_event: Callable = set_live[0]
    live_event: str = set_live[1]

    # intercepting reponses for live event
    replace_live_event(page, live_event)

    page.goto("/live")

    expect(page.locator("#mainnavigation.is-live").locator("#livebutton"),).to_have_css(
        name="background-color",
        value="rgb(255, 0, 0)",  # red
    )
