from pathlib import Path
from typing import Tuple, Callable
from playwright.sync_api import Page, expect, Locator, FrameLocator, Route

def test_live_indicator(
    page: Page,
    set_live: Callable,
    screenshot_dir: Path,
):
    # intercepting reponses for live event, and make live
    set_live(page)

#     # go to the live page
#     page.goto("/live")

    # validate live button is red
    expect(page.locator("#mainnavigation.is-live").locator("#livebutton"),).to_have_css(
        name="background-color",
        value="rgb(255, 0, 0)",  # red
    )

#     # waiting for peertube iframe to load
#     jbtube_video: FrameLocator = page.frame_locator("#liveStream")
#     video_player_peertube_icon: Locator = jbtube_video.locator(".peertube-dock-avatar")
#     expect(video_player_peertube_icon).to_be_visible()

#     page.evaluate("window.scrollTo(0, 0)")

    page.screenshot(path=f"{screenshot_dir}/live.png", full_page=True)


def test_mobile_live_indicator(
    mobile_device_tuple: Tuple[Page, str],
    set_live: Callable,
    screenshot_dir: Path,
):
    # set mobile page to variable
    mobile_device = mobile_device_tuple[0]
    # set screenshot dir for mobile device
    screenshot_dir = Path(
        screenshot_dir / f"mobile/{mobile_device_tuple[1].replace(' ','-')}/"
    )

    # intercepting reponses for live event, and make live
    set_live(mobile_device)

    mobile_device.goto("/live")

    navbar: Locator = mobile_device.locator("#mainnavigation.is-live",).locator(
        ".navbar-burger",
    )

    # wait for navbar to be visible
    expect(navbar).to_be_visible()

    # check if live indicator is red
    assert (
        navbar.evaluate(
            # integrated docs for python evaluate function:
            # https://github.com/microsoft/playwright/blob/a30aac56687598c373c51255308ef5833de0c9bb/docs/src/api/class-jshandle.md?plain=1#L77-L80
            # use evaluate function in python: https://playwright.dev/python/docs/api/class-page#page-evaluate
            # use getComputerStyle w/playwright: https://stackoverflow.com/a/71433333
            "element => window.getComputedStyle(element, ':before').backgroundColor"
        )
        == "rgb(255, 0, 0)"
    )

    # waiting for peertube iframe to load
    jbtube_video: FrameLocator = mobile_device.frame_locator("#liveStream")
    video_player_peertube_icon: Locator = jbtube_video.locator(".peertube-dock-avatar")
    expect(video_player_peertube_icon).to_be_visible()

    mobile_device.evaluate("window.scrollTo(0, 0)")

    mobile_device.screenshot(path=f"{screenshot_dir}/live-mobile.png", full_page=True)

    # click navbar to expand
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

    mobile_device.locator("#mainnavigation").locator(
        ".navbar-menu.is-active"
    ).screenshot(path=f"{screenshot_dir}/live-mobile_navbar.png")
