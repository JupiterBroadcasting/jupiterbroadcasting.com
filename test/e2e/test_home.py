import re
from datetime import datetime, timezone

from pytest import fixture
from playwright.sync_api import Page, expect

from episode_data import CONTENT_SHOW, _published, episodes_by_date, is_active


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/")


def test_homepage_has_logo(page: Page):
    """
    Ensure the large logo and text underneath it is visible on the screen
    """
    logo = page.locator(".logo")
    expect(logo).to_be_visible()

    logo_subtitle = page.locator('.subtitle')
    expect(logo_subtitle).to_contain_text(
        'Home to the best shows on Linux, Open Source, Security, Privacy, Community, Development, and News'
    )


def test_home_pagination(page: Page):
    """
    Ensure the pagination loads different episodes
    """
    first_card = page.locator('.card').nth(0).text_content
    page_2_button = page.locator('[aria-label="pagination"] >> text=2')
    page_2_button.click()
    page.wait_for_load_state("networkidle")
    assert "/page/2" in page.url
    first_card_second_page = page.locator('.card').nth(0).text_content
    assert first_card != first_card_second_page


def _expected_slides() -> list[str]:
    """
    One slide per active show, newest episode first (themes/jb/layouts/index.html).
    Future-dated episodes aren't built, so they don't count toward "newest"
    """
    now = datetime.now(timezone.utc)
    latest = {}
    for show_dir in CONTENT_SHOW.iterdir():
        if show_dir.is_dir() and is_active(show_dir):
            dates = [_published(e.data["date"]) for e in episodes_by_date(show_dir)]
            dates = [d for d in dates if d <= now]
            if dates:
                latest[show_dir.name] = max(dates)
    return [f"/show/{slug}/" for slug in sorted(latest, key=latest.get, reverse=True)]


def test_show_slider_slides(page: Page):
    slider = page.locator(".show-slider")
    expect(slider).to_have_class(re.compile(r"\bswiper-initialized\b"))
    hrefs = slider.locator(".swiper-slide a").evaluate_all("els => els.map(e => new URL(e.href).pathname)")
    assert hrefs == _expected_slides()


def _slider_at_start(page: Page):
    expect(page.locator(".show-slider .swiper-button-prev")).to_have_class(re.compile(r"\bswiper-button-disabled\b"))
    expect(page.locator(".show-slider .swiper-button-next")).not_to_have_class(re.compile(r"\bswiper-button-disabled\b"))


def _slider_moved(page: Page):
    # polls, so a slow transition under parallel load isn't read as "didn't move"
    page.wait_for_function(
        "() => new DOMMatrix(getComputedStyle(document.querySelector('.show-slider .swiper-wrapper')).transform).m41 < 0"
    )
    expect(page.locator(".show-slider .swiper-button-prev")).not_to_have_class(re.compile(r"\bswiper-button-disabled\b"))


def test_show_slider_buttons(page: Page):
    _slider_at_start(page)
    page.locator(".show-slider .swiper-button-next").click()
    _slider_moved(page)
    page.locator(".show-slider .swiper-button-prev").click()
    _slider_at_start(page)


def test_show_slider_drag(page: Page):
    """
    A mouse drag (Swiper's simulateTouch) moves the slider. The drag is held past Swiper's longSwipesMs (300ms):
    a quick flick can't be timed reliably under parallel load (Firefox's synthetic mouse took 538ms), and a held
    drag is what someone dragging with a mouse does anyway
    """
    _slider_at_start(page)
    box = page.locator(".show-slider").bounding_box()
    y = box["y"] + box["height"] / 2
    page.mouse.move(box["x"] + box["width"] * 0.8, y)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] * 0.5, y, steps=5)
    page.wait_for_timeout(600)
    page.mouse.move(box["x"] + box["width"] * 0.2, y, steps=5)
    page.mouse.up()
    expect(page.locator(".show-slider .swiper-button-prev")).not_to_have_class(re.compile(r"\bswiper-button-disabled\b"))
