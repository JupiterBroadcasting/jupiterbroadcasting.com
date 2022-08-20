import re
from playwright.sync_api import Page, expect


def test_homepage_screenshot(page: Page):
    page.goto("/")
    page.screenshot(path="screenshots/home.png", full_page=True)

def test_homepage_has_logo(page: Page):
    page.goto("/")
    logo = page.locator(".logo")
    expect(logo).to_be_visible()


    