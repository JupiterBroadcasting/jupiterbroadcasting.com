from typing import Dict, List
from urllib.parse import urlparse
from pytest import fixture, mark
from playwright.sync_api import Page, expect, Locator


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


def test_pagination(page: Page):
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


def test_rss_feeds(page: Page, expected_rss_feeds: List[Dict[str, str]]):
    """
    Ensure the RSS feeds menu contains all the fields specified in the conftest file
    """
    for rss_feed in expected_rss_feeds:
        element = page.locator('#rss-feeds-menu > div > a[href^="{}"]'.format(rss_feed['href']))
        expect(element).to_contain_text(rss_feed['title'])


@mark.dev
def test_dropdowns(page: Page, expected_dropdown_items: Dict[str, List[Dict[str, str]]]):
    """
    Tests dropdowns to make sure the dropdown items have links, and all items specified in conftest are present
    """
    for dropdown_text, child_elements in expected_dropdown_items.items():

        # dropdown item to hover over in menu
        parent_element: Locator = page.locator(f'.navbar-start >> a:has-text("{dropdown_text}"):visible')

        # hover to show elements
        parent_element.hover()

        # this is because Shows's url is show
        singular = dropdown_text.lower().rstrip('s')
        # test to make sure menu items hyperlink
        expect(parent_element).to_have_attribute('href', f'/{singular}/')

        # finds sibling element, which contains all the dropdown elements
        dropdown_elements: Locator = page.locator(f'a:has-text("{dropdown_text}") + .navbar-dropdown')

        for dropdown_item in child_elements:
            item: Locator = dropdown_elements.locator(f'a.navbar-item:has-text("{dropdown_item["title"]}")')
            try:
                # check if the path matches exactly what's in our expected output
                expect(item).to_have_attribute('href', dropdown_item['href'])
            except AssertionError:
                # if not, then it's a relative links (i.e. /community/irc/)
                #   so just comparing the path of the item
                assert urlparse(item.get_attribute('href')).path == dropdown_item['href']
            expect(item).to_be_visible()


def test_nav(page: Page, expected_dropdowns, expect_nav_items):
    """
    Test main navigation items
    """
    nav = page.locator('#mainnavigation')
    expect(nav).to_be_visible()
    dropdown_nav_items = page.locator('.navbar-start > * > a')
    count = dropdown_nav_items.count()
    for i in range(count):
        expect(dropdown_nav_items.nth(i)).to_contain_text(expected_dropdowns[i]['title'])
        expect(dropdown_nav_items.nth(i)).to_have_attribute('href', expected_dropdowns[i]['href'])

    nav_items = page.locator('.navbar-start > a')
    count = nav_items.count()
    for i in range(count):
        expect(nav_items.nth(i)).to_contain_text(expect_nav_items[i]['title'])
        expect(nav_items.nth(i)).to_have_attribute('href', expect_nav_items[i]['href'])

    nav_image = page.locator('.navbar-brand > a > img')

    expect(nav_image.nth(0)).to_be_visible()
