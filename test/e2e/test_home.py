from pytest import fixture
from playwright.sync_api import Page, expect


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
