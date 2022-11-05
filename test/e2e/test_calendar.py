from pathlib import Path
from pytest import fixture
from playwright.sync_api import Page, expect, FrameLocator, Locator


"""
Code here will run for every test in this file
"""
@fixture(autouse=True)
def setup(page: Page):
    page.goto("/calendar")
    page.wait_for_load_state("networkidle")


"""
Take a screenshot of the calendar page for manual review
"""
def test_calendar_screenshot(page: Page, screenshot_dir: Path):
    page.screenshot(path=f"{screenshot_dir}/calendar.png", full_page=True)

