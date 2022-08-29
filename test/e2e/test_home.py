import re
from pathlib import Path
from typing import Dict, List
from playwright.sync_api import Page, expect

def test_homepage_screenshot(page: Page, screenshot_dir: Path):
    page.goto("/")
    page.pause()
    page.screenshot(path=f"{screenshot_dir}/home.png", full_page=True)

def test_homepage_has_logo(page: Page):
    page.goto("/")
    logo = page.locator(".logo")
    expect(logo).to_be_visible()

    logo_subtitle = page.locator('.subtitle')
    expect(logo_subtitle).to_contain_text('Home to the best shows on Linux, Open Source, Security, Privacy, Community, Development, and News')

def test_pagination(page: Page):
    page.goto("/")
    first_card = page.locator('.card').nth(0).text_content
    page_2_button = page.locator('[aria-label="pagination"] >> text=2')
    page_2_button.click()
    page.wait_for_load_state("networkidle")
    assert "/page/2" in page.url
    first_card_second_page = page.locator('.card').nth(0).text_content
    assert first_card != first_card_second_page

def test_rss_feeds(page: Page, expected_rss_feeds: List[Dict[str,str]]):
    page.goto("/")

    for rss_feed in expected_rss_feeds:
        element = page.locator('#rss-feeds-menu > div > a[href^="{}"]'.format(rss_feed['href']))
        expect(element).to_contain_text(rss_feed['title'])


def test_dropdowns(page: Page, expected_dropdown_items):
    page.goto("/")

    for dropdown_item in expected_dropdown_items:
        selector = '.navbar-item > .navbar-dropdown > a[href^="{}"]'.format(dropdown_item['href'])
        element = page.locator(selector)
        expect(element).to_contain_text(dropdown_item['title'])
    


def test_nav(page: Page, expected_dropdowns, expect_nav_items):

    page.goto("/")
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