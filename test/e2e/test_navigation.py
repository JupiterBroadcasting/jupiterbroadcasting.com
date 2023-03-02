from urllib.parse import urlparse
from pytest import fixture
from playwright.sync_api import Page, expect, Locator


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/")


def test_nav_rss_feeds(page: Page, expected_rss_feeds: list[dict[str, str]]):
    """
    Ensure the RSS feeds menu contains all the fields specified in the conftest file
    """
    for rss_feed in expected_rss_feeds:
        element = page.locator('#rss-feeds-menu > div > a[href^="{}"]'.format(rss_feed['href']))
        expect(element).to_contain_text(rss_feed['title'])


def test_nav_dropdowns(page: Page, expected_dropdown_items: dict[str, list[dict[str, str]]]):
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
