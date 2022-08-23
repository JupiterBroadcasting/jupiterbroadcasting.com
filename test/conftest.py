from pathlib import Path
from typing import Dict, List
from pytest import fixture
from playwright.sync_api import Page
from urllib.parse import urlparse

def base_url(page: Page):
    parsed_url = urlparse(page.url)
    return "{}://{}".format(parsed_url.scheme, parsed_url.netloc)

@fixture
def screenshot_dir() -> Path:
    return Path('screenshots/')

@fixture
def expected_rss_feeds() -> List[Dict[str,str,]]:
    return [
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
    ]