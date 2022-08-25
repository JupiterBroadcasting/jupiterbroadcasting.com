<<<<<<< HEAD:test/e2e/home.py
import re
from playwright.sync_api import Page, expect
<<<<<<< HEAD
=======
from pathlib import Path
from typing import Dict, List
from pytest import fixture
from playwright.sync_api import Page
>>>>>>> 1c5f94a1e172510a3f55ae85ee94ed0f86d60d1c:test/conftest.py
from urllib.parse import urlparse

def base_url(page: Page):
    parsed_url = urlparse(page.url)
    return "{}://{}".format(parsed_url.scheme, parsed_url.netloc)
=======
>>>>>>> feat/e2e_tests

@fixture
def screenshot_dir() -> Path:
    return Path('screenshots/')

<<<<<<< HEAD:test/e2e/home.py
def test_homepage_screenshot(page: Page):
    page.goto("/")
<<<<<<< HEAD
    page.pause()
=======
>>>>>>> feat/e2e_tests
    page.screenshot(path="screenshots/home.png", full_page=True)

def test_homepage_has_logo(page: Page):
    page.goto("/")
    logo = page.locator(".logo")
    expect(logo).to_be_visible()

<<<<<<< HEAD
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

def test_rss_feeds(page: Page):
    page.goto("/")
    expected_rss_feeds = [
=======
@fixture
def expected_rss_feeds() -> List[Dict[str,str,]]:
    return [
>>>>>>> 1c5f94a1e172510a3f55ae85ee94ed0f86d60d1c:test/conftest.py
        { 'href': 'http://feeds2.feedburner.com/JupiterBroadcasting', 'title': 'All Shows Feed - Audio'},
        { 'href': 'http://feeds2.feedburner.com/AllJupiterVideos', 'title': 'All Shows Feed - Video'},
        { 'href': 'https://coder.show/rss', 'title': 'Coder Radio'},
        { 'href': 'https://extras.show/rss', 'title': 'Jupiter EXTRAS'},
        { 'href': 'https://linuxactionnews.com/rss', 'title': 'Linux Action News'},
        { 'href': 'https://linuxunplugged.com/rss', 'title': 'LINUX Unplugged'},
        { 'href': 'https://www.officehours.hair/rss', 'title': 'Office Hours'},
        { 'href': 'https://selfhosted.show/rss', 'title': 'Self-Hosted'}
    ]

@fixture
def expected_dropdown_items(base_url) -> List[Dict[str,str]]:
    return [
        {'href': '/hosts', 'title': 'Hosts'},
        {'href': '/guests', 'title': 'Guests'},
        {'href': 'https://github.com/JupiterBroadcasting/', 'title': 'GitHub'},
        {'href': 'https://jupiter.tube', 'title': 'Peertube'},
        {'href': 'https://www.meetup.com/jupiterbroadcasting', 'title': 'Meetup'},
        {'href': 'https://www.youtube.com/user/jupiterbroadcasting', 'title': 'YouTube'},
        {'href': 'https://twitter.com/jupitersignal', 'title': 'Twitter'},
        {'href': '{}/community/irc'.format(base_url), 'title': 'IRC'},
        {'href': 'http://www.facebook.com/pages/Jupiter-Broadcasting/156241429615', 'title': 'Facebook'},
        {'href': 'https://discord.com/invite/n49fgkp', 'title': 'Self-Hosted Discord'},
        {'href': '{}/community/matrix'.format(base_url), 'title': 'Matrix'},
        {'href': '{}/community/mumble'.format(base_url), 'title': 'Mumble'},
        {'href': 'https://t.me/jupitertelegram', 'title': 'Telegram'},
        {'href': '/show/coder-radio', 'title': 'Coder Radio'},
        {'href': '/show/jupiter-extras', 'title': 'Jupiter EXTRAS'},
        {'href': '/show/linux-action-news', 'title': 'Linux Action News'},
        {'href': '/show/linux-unplugged', 'title': 'LINUX Unplugged'},
        {'href': '/show/office-hours', 'title': 'Office Hours'},
        {'href': '/show/self-hosted', 'title': 'Self-Hosted'},
    ]

@fixture
def expected_dropdowns() -> List[Dict[str,str]]:
    return [
        {'title': 'Shows', 'href': '/show'},
        {'title': 'People', 'href': "/people"},
        {'title': 'Community', 'href': "/community"}
    ]

@fixture
def expect_nav_items() -> List[Dict[str,str]]:
    return [
        {'title': 'Sponsors', 'href': '/sponsors'},
        {'title': 'Live', 'href': 'https://jb-live.jupiterbroadcasting.net/'},
        {'title': 'Calendar', 'href': '/calendar'},
        {'title': 'Boost!', 'href': '/boost'},
        {'title': 'Garage Sale', 'href': 'https://www.jupitergarage.com/'},
        {'title': 'Membership', 'href': '/membership'},
        {'title': 'Archive', 'href': '/archive'},
        {'title': 'Contact', 'href': '/contact'},
<<<<<<< HEAD:test/e2e/home.py
    ]


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





=======
>>>>>>> feat/e2e_tests

    
=======
    ]
>>>>>>> 1c5f94a1e172510a3f55ae85ee94ed0f86d60d1c:test/conftest.py
