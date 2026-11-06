from typing import Tuple

from pytest import mark
from playwright.sync_api import Page, expect

# matches Bulma's $tablet (themes/jb/assets/css/libs/bulma/sass/utilities/initial-variables.sass)
BULMA_TABLET = 769

OVERFLOW_PAGES = [
    "/",
    "/show/linux-unplugged/",
    "/show/linux-unplugged/434/",
    "/people/",
]

# lup 434 has sponsors, hosts and guests
EPISODE = "/show/linux-unplugged/434/"


def _overflowing(page: Page) -> list[str]:
    # compare against the emulated device width, not innerWidth: mobile Chromium widens the
    #   layout viewport to fit overflowing content, which would hide the bug
    width = page.viewport_size["width"]
    return page.evaluate(
        """width => {
            const over = e => e && e.getBoundingClientRect().right > width + 1;
            const inFixed = e => { for (; e; e = e.parentElement) if (getComputedStyle(e).position === 'fixed') return true; return false; };
            // outermost offenders only: children of an overflowing element just inherit its overflow
            return [...document.querySelectorAll('body *')]
            .filter(e => e.getBoundingClientRect().width > 0 && over(e) && !over(e.parentElement) && !inFixed(e))
            .map(e => `${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}.${[...e.classList].join('.')}`)
            .slice(0, 10);
        }""",
        width,
    )


def test_mobile_burger_menu(mobile_device_tuple: Tuple[Page, str]):
    """
    Every device is under the 1220px navbar breakpoint, so the menu is collapsed behind the burger
    """
    page, _ = mobile_device_tuple
    page.goto("/")
    burger = page.locator(".navbar-burger")
    menu = page.locator("#navbarBasicExample")
    contact = menu.locator('a.navbar-item[href$="/contact/"]')

    expect(burger).to_be_visible()
    expect(burger).to_have_attribute("aria-expanded", "false")
    expect(contact).to_be_hidden()

    burger.click()
    expect(menu).to_have_class("navbar-menu is-active")
    expect(burger).to_have_attribute("aria-expanded", "true")
    expect(contact).to_be_visible()
    expect(menu.locator('a.navbar-item[href$="/show/linux-unplugged/"]')).to_be_visible()

    burger.click()
    expect(burger).to_have_attribute("aria-expanded", "false")
    expect(contact).to_be_hidden()


@mark.parametrize("path", OVERFLOW_PAGES)
def test_mobile_no_horizontal_overflow(mobile_device_tuple: Tuple[Page, str], path: str):
    page, _ = mobile_device_tuple
    page.goto(path, wait_until="domcontentloaded")
    width = page.viewport_size["width"]
    assert page.evaluate("document.documentElement.scrollWidth") <= width, _overflowing(page)


def test_mobile_episode_sponsor_block(mobile_device_tuple: Tuple[Page, str]):
    """
    The episode page renders sponsors twice; the copy above the content only shows below Bulma's tablet width
    """
    page, _ = mobile_device_tuple
    page.goto(EPISODE, wait_until="domcontentloaded")
    visible = page.locator(".sponsor-list:visible")
    expect(visible).to_have_count(1)
    in_mobile_block = page.locator(".is-hidden-tablet .sponsor-list:visible")
    expect(in_mobile_block).to_have_count(1 if page.viewport_size["width"] < BULMA_TABLET else 0)


def test_mobile_episode_player_fits(mobile_device_tuple: Tuple[Page, str]):
    page, _ = mobile_device_tuple
    page.goto(EPISODE, wait_until="domcontentloaded")
    player = page.locator("#pv-embed-player")
    expect(player).to_be_visible()
    box = player.bounding_box()
    assert box["x"] >= 0 and box["x"] + box["width"] <= page.viewport_size["width"] + 1, box
