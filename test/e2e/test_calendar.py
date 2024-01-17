from pytest import fixture
from playwright.sync_api import Page, expect, FrameLocator, Locator


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/calendar")
    page.wait_for_load_state("networkidle")
