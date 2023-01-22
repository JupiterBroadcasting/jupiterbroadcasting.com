from pathlib import Path
from pytest import fixture
from playwright.sync_api import Page, expect


"""
Code here will run for every test in this file
"""
@fixture(autouse=True)
def setup(page: Page):
    page.goto("/404.html")  # TODO: Change to random address once #483 is merged


"""
Take a screenshot of the 404 page for manual review
"""
def test_404_screenshot(page: Page, screenshot_dir: Path):
    page.screenshot(path=f"{screenshot_dir}/404.png", full_page=True)


"""
Ensure text "Page Not Found" and unicorn image is present on the 404 page
"""
def test_404_contents(page: Page):
    title = page.locator(".title.has-text-centered")
    expect(title).to_contain_text("Page Not Found")

    unicorn = page.locator("#img-404")
    expect(unicorn).to_be_visible()
