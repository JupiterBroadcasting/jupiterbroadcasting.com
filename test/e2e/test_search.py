from pathlib import Path
import pytest
from playwright.sync_api import Page, expect


def search(page: Page, query: str):
    page.goto("/search/")
    page.fill("#search-input", query)


def test_search_screenshot(page: Page, screenshot_dir: Path):
    search(page, "add water")
    expect(page.locator(".search-result").first).to_be_visible()
    page.screenshot(path=f"{screenshot_dir}/search.png", full_page=True)


def test_pick_ranks_first(page: Page):
    search(page, "add water")
    first = page.locator(".search-result").first
    expect(first).to_have_attribute("data-type", "pick")
    expect(first.locator("a").first).to_have_attribute("href", "https://flathub.org/apps/dev.qwery.AddWater")


def test_sponsor_ranks_first(page: Page):
    search(page, "1password")
    expect(page.locator(".search-result").first).to_have_attribute("data-type", "sponsor")


def test_episode_title_found(page: Page):
    search(page, "All Your Kernels Belong to Rust")
    episode = page.locator('.search-result[data-type="episode"] a[href*="/show/linux-unplugged/603"]')
    expect(episode.first).to_be_visible()


def test_person_found(page: Page):
    search(page, "Hannah Anderson")
    expect(page.locator('.search-result[data-type="person"]').first).to_be_visible()


def test_empty_query_shows_nothing(page: Page):
    search(page, "add water")
    expect(page.locator(".search-result").first).to_be_visible()
    page.fill("#search-input", "   ")
    expect(page.locator("#search-results > *")).to_have_count(0)
    expect(page.locator("#search-status")).to_have_text("")


def test_no_results_message(page: Page):
    search(page, "xkcdqzv 77777")
    expect(page.locator("#search-status")).to_have_text("No results")


def test_markup_is_escaped(page: Page):
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d), d.dismiss()))
    search(page, "<script>")
    page.wait_for_timeout(1000)
    assert page.locator("#search-results script").count() == 0
    assert dialogs == []


def test_stale_results_do_not_overwrite(page: Page):
    page.goto("/search/")
    page.type("#search-input", "add water")
    page.fill("#search-input", "1password")
    page.wait_for_timeout(1500)
    expect(page.locator(".search-result").first).to_have_attribute("data-type", "sponsor")


def test_episode_shows_show_chip(page: Page):
    search(page, "All Your Kernels Belong to Rust")
    episode = page.locator('.search-result[data-type="episode"]').first
    expect(episode.locator(".tag").nth(1)).to_have_text("LINUX Unplugged")


def test_newer_episodes_rank_above_older(page: Page):
    search(page, "home assistant")
    dates = page.locator('.search-result[data-type="episode"] .search-muted')
    expect(dates.first).to_be_visible()
    texts = dates.all_inner_texts()
    assert texts[0] >= "2020-01-01", texts[:5]


@pytest.mark.parametrize("query,type_", [
    ("linux unplugged", "show"),
    ("coder radio", "show"),
    ("alex kretzschmar", "person"),
    ("brent gervais", "person"),
])
def test_show_and_person_title_matches_rank_first(page: Page, query: str, type_: str):
    search(page, query)
    expect(page.locator(".search-result").first).to_have_attribute("data-type", type_)


def test_pick_ranks_above_show(page: Page):
    search(page, "tailscale")
    expect(page.locator(".search-result").first).to_have_attribute("data-type", "sponsor")


def test_show_indexed_once(page: Page):
    search(page, "linux unplugged")
    expect(page.locator(".search-result").first).to_have_attribute("data-type", "show")
    expect(page.locator('.search-result[data-type="show"] a[href*="/show/linux-unplugged"]')).to_have_count(1)


def test_host_who_was_guest_indexed_once(page: Page):
    search(page, "wes payne")
    expect(page.locator(".search-result").first).to_have_attribute("data-type", "person")
    expect(page.locator('.search-result[data-type="person"]')).to_have_count(1)
