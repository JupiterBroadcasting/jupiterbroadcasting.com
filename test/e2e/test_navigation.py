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
    Ensure dropdowns on the page match conftest exactly (no missing or unexpected items) and every item links correctly
    """
    dropdowns: Locator = page.locator('.navbar-start >> .has-dropdown:visible')
    dropdowns_list: list[str] = [dropdown.locator('> a.navbar-link').text_content().strip() for dropdown in dropdowns.all()]
    expected_list = [dropdown for dropdown in expected_dropdown_items]

    if (len(difference:=set(dropdowns_list) ^ set(expected_list))):
        if (len(unexpected:={dropdown for dropdown in dropdowns_list if dropdown in difference})):
            raise KeyError (f'Dropdown(s) {list(unexpected)} missing from expected list')
        else:
            unexpected = {dropdown for dropdown in expected_list if dropdown in difference}
            raise KeyError (f'Expected Dropdown(s) {list(unexpected)} missing from the page')

    for parent in dropdowns.all():
        parent.hover()
        dropdown = parent.locator('a.navbar-link').first

        parent_item: str = dropdown.text_content().strip()

        children: Locator = parent.locator('.navbar-dropdown >> .navbar-item')
        for childitem in children.all():
            childitem_text: str = childitem.text_content().strip()

            expected_dropdown = expected_dropdown_items.get(parent_item, None)

            if expected_dropdown is None:
                raise KeyError(f'{parent_item} is not a expected dropdown')

            expected: dict[str, str] = next(filter(lambda item: item['title'] == childitem_text , expected_dropdown), None)

            if expected is None:
                raise KeyError(f'{childitem_text} is not in expected dropdown items')

            if expected['href'][0] == '/':
                assert urlparse(childitem.get_attribute('href')).path == expected['href']
            else:
                assert childitem.get_attribute('href') == expected['href']

            expect(childitem).to_be_visible()


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
