from pytest import fixture
from playwright.sync_api import Page, expect


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/404.html")  # TODO: Change to random address once #483 is merged


def test_404_contents(page: Page):
    """
    Ensure text "Page Not Found" and unicorn image is present on the 404 page
    """
    title = page.locator(".title.has-text-centered")
    expect(title).to_contain_text("Page Not Found")

    unicorn = page.locator("#img-404")
    expect(unicorn).to_be_visible()
