
from pathlib import Path
from typing import Dict, Generator, List
from pytest import fixture
from pytest_base_url.plugin import base_url
from playwright.sync_api import Playwright, APIRequestContext

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
def expected_dropdown_items() -> Dict[str,List[Dict[str,str]]]:
    return {
        "Shows": [
            {'href': '/show/coder-radio/', 'title': 'Coder Radio'},
            {'href': '/show/jupiter-extras/', 'title': 'Jupiter EXTRAS'},
            {'href': '/show/linux-action-news/', 'title': 'Linux Action News'},
            {'href': '/show/linux-unplugged/', 'title': 'LINUX Unplugged'},
            {'href': '/show/office-hours/', 'title': 'Office Hours'},
            {'href': '/show/self-hosted/', 'title': 'Self-Hosted'},
        ],
        "People": [
            {'href': '/hosts/', 'title': 'Hosts'},
            {'href': '/guests/', 'title': 'Guests'},
        ],
        "Community": [
            {'href': 'https://github.com/JupiterBroadcasting/', 'title': 'GitHub'},
            {'href': 'https://jupiter.tube', 'title': 'Peertube'},
            {'href': 'https://www.meetup.com/jupiterbroadcasting/', 'title': 'Meetup'},
            {'href': 'https://www.youtube.com/user/jupiterbroadcasting', 'title': 'YouTube'},
            {'href': 'https://twitter.com/jupitersignal', 'title': 'Twitter'},
            {'href': '/community/irc/', 'title': 'IRC'},
            {'href': 'http://www.facebook.com/pages/Jupiter-Broadcasting/156241429615', 'title': 'Facebook'},
            {'href': 'https://discord.com/invite/n49fgkp', 'title': 'Self-Hosted Discord'},
            {'href': '/community/matrix/', 'title': 'Matrix'},
            {'href': '/community/mumble/', 'title': 'Mumble'},
            {'href': 'https://t.me/jupitertelegram', 'title': 'Telegram'},
        ]
    }

@fixture
def expected_dropdowns() -> List[Dict[str,str]]:
    return [
        {'title': 'Shows', 'href': '/show/'},
        {'title': 'People', 'href': "/people/"},
        {'title': 'Community', 'href': "/community/"}
    ]

@fixture
def expect_nav_items() -> List[Dict[str,str]]:
    return [
        {'title': 'Sponsors', 'href': '/sponsors/'},
        {'title': 'Live', 'href': '/live/'},
        {'title': 'Calendar', 'href': '/calendar/'},
        {'title': 'Boost!', 'href': '/boost/'},
        {'title': 'Garage Sale', 'href': 'https://www.jupitergarage.com/'},
        {'title': 'Membership', 'href': '/membership/'},
        # commenting out for now PR #399
        # {'title': 'Archive', 'href': '/archive'},
        # failing on tests here: https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/runs/8254156209?check_suite_focus=true#step:9:26
        {'title': 'Contact', 'href': '/contact/'},
    ]

# https://playwright.dev/python/docs/api-testing#configure
# used for doing similar requests to API calls
@fixture(scope="session")
def api_request_context(
    # base playwright context/object
    playwright: Playwright,
    # from the pytest-base-url plugin Playwright installs (automatically)
    #   so we're not having to hard-code the URL
    base_url: base_url,
    # Generator is returned based on Playwright docs
) -> Generator[APIRequestContext, None, None]:
    # creates APIRequestContext to allow requests to be made
    #   using the base_url variable (from the plugin) to define
    #   the base_url which'll allow requests relative to that base_url
    request_context = playwright.request.new_context(base_url=base_url)
    # essentially a "return", but used with generators
    yield request_context
    # supposed to get rid of coookies/other stored info after generator is done
    # https://playwright.dev/python/docs/api/class-apirequestcontext#api-request-context-dispose
    # https://github.com/microsoft/playwright.dev/blob/d9b4a2f3bd0510ea89c87ed230b8241eb33b6688/python/docs/api-testing.mdx#writing-api-test
    request_context.dispose()
