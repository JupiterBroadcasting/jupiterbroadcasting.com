import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse
from pytest import fixture, mark
from playwright.sync_api import Page, expect, Locator

# allows this to be run for every test in this file,
#   without it needing to specify it
@fixture(autouse=True)
def setup(page: Page):
    page.goto("/")

def test_homepage_screenshot(page: Page, screenshot_dir: Path):
    page.screenshot(path=f"{screenshot_dir}/home.png", full_page=True)

def test_homepage_has_logo(page: Page):
    logo = page.locator(".logo")
    expect(logo).to_be_visible()

    logo_subtitle = page.locator('.subtitle')
    expect(logo_subtitle).to_contain_text('Home to the best shows on Linux, Open Source, Security, Privacy, Community, Development, and News')

def test_pagination(page: Page):
    first_card = page.locator('.card').nth(0).text_content
    page_2_button = page.locator('[aria-label="pagination"] >> text=2')
    page_2_button.click()
    page.wait_for_load_state("networkidle")
    assert "/page/2" in page.url
    first_card_second_page = page.locator('.card').nth(0).text_content
    assert first_card != first_card_second_page

def test_rss_feeds(page: Page, expected_rss_feeds: List[Dict[str,str]]):
    for rss_feed in expected_rss_feeds:
        element = page.locator('#rss-feeds-menu > div > a[href^="{}"]'.format(rss_feed['href']))
        expect(element).to_contain_text(rss_feed['title'])


def test_dropdowns(page: Page, expected_dropdown_items: Dict[str,List[Dict[str,str]]]):
    dropdowns: Locator = page.locator('.navbar-start >> .has-dropdown:visible')
    assert dropdowns.count() == len(expected_dropdown_items), 'Number of actual dropdowns does not match expected number of dropdowns'

    for dropdown_index in range(dropdowns.count()):
        parent = dropdowns.nth(dropdown_index)
        parent.hover()
        dropdown = parent.locator('a.navbar-link').first

        parent_item: str = dropdown.text_content().strip()

        children: Locator = parent.locator('.navbar-dropdown >> .navbar-item')
        for child_index in range(children.count()):
            childitem: Locator = children.nth(child_index)
            childitem_text: str = childitem.text_content().strip()

            expected_dropdown = expected_dropdown_items.get(parent_item, None)

            if expected_dropdown is None:
                raise KeyError(f'{parent_item} is not a expected dropdown')

            expected: Dict[str,str] = next(filter(lambda item: item['title'] == childitem_text , expected_dropdown), None)

            if expected is None:
                raise KeyError(f'{childitem_text} is not in expected dropdown items')

            if expected['href'][0] == '/':
                assert urlparse(childitem.get_attribute('href')).path == expected['href']
            else:
                assert childitem.get_attribute('href') == expected['href']

            expect(childitem).to_be_visible()

def test_nav(page: Page, expected_dropdowns, expect_nav_items):

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
