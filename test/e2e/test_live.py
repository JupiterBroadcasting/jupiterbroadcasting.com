from typing import Tuple, Callable
from pytest import mark
from playwright.sync_api import Page, expect, Locator


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


def test_mobile_live_indicator(
    mobile_device: Page,
    set_live: Tuple[Callable, str],
):
    # explicitly defining tuple objects for clarity
    replace_live_event: Callable = set_live[0]
    live_event: str = set_live[1]

    # intercepting reponses for live event
    replace_live_event(mobile_device, live_event)

    mobile_device.goto("/live")

    navbar: Locator = mobile_device.locator("#mainnavigation.is-live",).locator(
        ".navbar-burger",
    )

    # wait for navbar to be visible
    expect(navbar).to_be_visible()

    # check if live indicator is red
    assert (
        navbar.evaluate(
            # integrated docs for python evaluate function: https://github.com/microsoft/playwright/blob/a30aac56687598c373c51255308ef5833de0c9bb/docs/src/api/class-jshandle.md?plain=1#L77-L80
            # use evaluate function in python: https://playwright.dev/python/docs/api/class-page#page-evaluate
            # use getComputerStyle w/playwright: https://stackoverflow.com/a/71433333
            "element => window.getComputedStyle(element, ':before').backgroundColor"
        )
        == "rgb(255, 0, 0)"
    )

    navbar.click()

    # repeat test_live_indicator for mobile device
    expect(
        mobile_device.locator("#mainnavigation.is-live",).locator(
            "#livebutton",
        ),
    ).to_have_css(
        name="background-color",
        value="rgb(255, 0, 0)",  # red
    )
