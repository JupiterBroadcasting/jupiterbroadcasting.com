from pathlib import Path
from typing import Generator, Callable
from pytest import fixture
from _pytest.fixtures import SubRequest
from pytest_base_url.plugin import base_url
from playwright.sync_api import Playwright, APIRequestContext, Route, Page, Browser
import json


@fixture
def get_test_dir() -> Path:
    return Path(__file__).parent.absolute()


@fixture
def screenshot_dir() -> Path:
    return Path('screenshots/')

# identified all possible device types by running the following in a
#   python interpreter + shell commands
"""
# python interpreter
with sync_playwright() as playwright:
    Path('./devices.json').write_text(j_dumps(playwright.devices, indent=2))

# shell cmd
jq '. | keys' devices.json| less
"""
# also should be able to view them here:
# https://github.com/microsoft/playwright/blob/v1.25.2/packages/playwright-core/src/server/deviceDescriptorsSource.json
@fixture(
    # doing session so it doesn't have to be re-created for each usage
    scope="session",
    # some example phone sizes to use
    params=[
        "iPhone 13",
        "Pixel 5",
        "Galaxy S9+",
    ]
)
def mobile_device_tuple(
    # how to access the params
    request: SubRequest,
    # browser object given by playwright built-in fixture
    browser: Browser,
    # Playwright object given by playwright built-in fixture
    playwright: Playwright,
    # from the pytest-base-url plugin Playwright installs (automatically)
    #   so we're not having to hard-code the URL
    base_url: base_url,
) -> tuple[Page,str]:
    """
    identified all possible device types by running the following in a python interpreter + shell commands

    # python interpreter
    with sync_playwright() as playwright:
        Path('./devices.json').write_text(j_dumps(playwright.devices, indent=2))

    # shell cmd
    jq '. | keys' devices.json| less

    also should be able to view them here:
    https://github.com/microsoft/playwright/blob/v1.25.2/packages/playwright-core/src/server/deviceDescriptorsSource.json
    """

    # based on here: https://playwright.dev/python/docs/emulation#devices
    context = browser.new_context(
        base_url=base_url,
        # based on this info: https://playwright.dev/python/docs/emulation#devices
        **playwright.devices[request.param]
    )
    try:
        # essentially a "return", but used with generators
        yield context.new_page(), request.param
    except Exception as e:
        raise e
    finally:
        # supposed to get rid of cookies/other stored info after generator is done
        # https://playwright.dev/python/docs/api/class-apirequestcontext#api-request-context-dispose
        # https://github.com/microsoft/playwright.dev/blob/d9b4a2f3bd0510ea89c87ed230b8241eb33b6688/python/docs/api-testing.mdx#writing-api-test
        context.close()


@fixture(scope="session")
def api_request_context(
        playwright: Playwright,  # base playwright context/object
        # From the pytest-base-url plugin Playwright installs (automatically) so we're not having to hard-code the URL
        base_url: base_url,
) -> Generator[APIRequestContext, None, None]:  # Generator is returned based on Playwright docs
    """
    https://playwright.dev/python/docs/api-testing#configure
    used for doing similar requests to API calls
    """
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


@fixture(
    # doing session so it doesn't have to be re-created for each usage
    scope="session",
    # some example phone sizes to use
    params=[
        "iPhone 13",
        "Pixel 5",
        "Galaxy S9+",
    ]
)
def mobile_device_tuple(
        # how to access the params
        request: SubRequest,
        # browser object given by playwright built-in fixture
        browser: Browser,
        # Playwright object given by playwright built-in fixture
        playwright: Playwright,
        # from the pytest-base-url plugin Playwright installs (automatically)
        #   so we're not having to hard-code the URL
        base_url: base_url,
) -> tuple[Page, str]:
    """
    identified all possible device types by running the following in a python interpreter + shell commands

    # python interpreter
    with sync_playwright() as playwright:
        Path('./devices.json').write_text(j_dumps(playwright.devices, indent=2))

    # shell cmd
    jq '. | keys' devices.json| less

    also should be able to view them here:
    https://github.com/microsoft/playwright/blob/v1.25.2/packages/playwright-core/src/server/deviceDescriptorsSource.json
    """
    params=playwright.devices[request.param]


    # based on here: https://playwright.dev/python/docs/emulation#devices
    params = playwright.devices[request.param]
    if browser.browser_type.name == "firefox":
        # bug in playwright for firefox https://github.com/microsoft/playwright/issues/16622
        # https://github.com/Lookyloo/PlaywrightCapture/blob/34ab2c3e096fc3bc1ebef217063b78f3554d8a42/playwrightcapture/capture.py#L188
        del params['is_mobile']

    context = browser.new_context(
        base_url=base_url,
        # based on this info: https://playwright.dev/python/docs/emulation#devices
        **params
    )
    try:
        # essentially a "return", but used with generators
        yield context.new_page(), request.param
    except Exception as e:
        raise e
    finally:
        # supposed to get rid of cookies/other stored info after generator is done
        # https://playwright.dev/python/docs/api/class-apirequestcontext#api-request-context-dispose
        # https://github.com/microsoft/playwright.dev/blob/d9b4a2f3bd0510ea89c87ed230b8241eb33b6688/python/docs/api-testing.mdx#writing-api-test
        context.close()


@fixture(scope="session")
def api_request_context(
        playwright: Playwright,  # base playwright context/object
        # From the pytest-base-url plugin Playwright installs (automatically) so we're not having to hard-code the URL
        base_url: base_url,
) -> Generator[APIRequestContext, None, None]:  # Generator is returned based on Playwright docs
    """
    https://playwright.dev/python/docs/api-testing#configure
    used for doing similar requests to API calls
    """
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


@fixture
def expected_rss_feeds() -> list[dict[str, str, ]]:
    return [
        {'href': 'http://feeds2.feedburner.com/JupiterBroadcasting', 'title': 'All Shows Feed - Audio'},
        {'href': 'http://feeds2.feedburner.com/AllJupiterVideos', 'title': 'All Shows Feed - Video'},
        {'href': 'https://coder.show/rss', 'title': 'Coder Radio'},
        {'href': 'https://extras.show/rss', 'title': 'Jupiter EXTRAS'},
        {'href': 'https://linuxactionnews.com/rss', 'title': 'Linux Action News'},
        {'href': 'https://linuxunplugged.com/rss', 'title': 'LINUX Unplugged'},
        {'href': 'https://www.officehours.hair/rss', 'title': 'Office Hours'},
        {'href': 'https://selfhosted.show/rss', 'title': 'Self-Hosted'}
    ]


@fixture
def expected_dropdown_items() -> dict[str, list[dict[str, str]]]:
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
def expected_dropdowns() -> list[dict[str, str]]:
    return [
        {'title': 'Shows', 'href': '/show/'},
        {'title': 'People', 'href': "/people/"},
        {'title': 'Community', 'href': "/community/"}
    ]


@fixture
def expect_nav_items() -> list[dict[str, str]]:
    return [
        {'title': 'Sponsors', 'href': '/sponsors/'},
        {'title': 'Live', 'href': '/live/'},
        {'title': 'Calendar', 'href': '/calendar/'},
        {'title': 'Boost!', 'href': '/boost/'},
        {'title': 'Garage Sale', 'href': 'https://www.jupitergarage.com/'},
        {'title': 'Membership', 'href': '/membership/'},
        # commenting out for now PR #399
        # {'title': 'Archive', 'href': '/archive'},
        # failing on tests here:
        # https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/runs/8254156209?check_suite_focus=true#step:9:26
        {'title': 'Contact', 'href': '/contact/'},
    ]


@fixture
def set_live() -> Callable:
    return _replace_live_event

@staticmethod
def _replace_live_event(page: Page) -> None:
    def handle_route(route: Route) -> None:
        # fetch original response
        response = page.request.fetch(route.request)
        json_data = response.json()

        # override response values
        if json_data.get('data'):
            json_data['data'][0]['isLive'] = True
        json_data['total'] = 1

        # setting live event
        route.fulfill(
            # Pass all fields from the response
            response=response,
            body=json.dumps(json_data),
        )
    page.route(
        "https://jupiter.tube/api/v1/video-channels/live/**",
        handle_route
    )


@fixture
def live_event_json(get_test_dir: Path) -> str:
    return Path(get_test_dir / 'fixture_files/jb-live_sample-live-event.json').read_text()

@fixture 
def replace_live_event(page: Page) -> Callable:
    def handle_route(route: Route, p: Page, live_event: str) -> Callable[[Page, str], None]:
        # fetch original response
        response = p.request.fetch(route.request)

        # setting live event
        route.fulfill(
            # Pass all fields from the response
            response=response,
            # override body
            body=live_event.strip()
        )
    
    def mock_jb_tube_request(p: Page, live_event: str):
        p.route(
        "https://jupiter.tube/api/v1/video-channels/live/videos?isLive=true&skipCount=false&count=1&sort=-createdAt",
        lambda route: handle_route(route, p, live_event)
    ) 

    return mock_jb_tube_request


@fixture
def set_live(get_live_event: str) -> tuple[Callable, str]:
    return _replace_live_event, get_live_event
# return replace_live_event


@staticmethod
def _replace_live_event(page: Page, live_event: str) -> None:
    def handle_route(route: Route) -> None:
        # fetch original response
        response = page.request.fetch(route.request)

        # setting live event
        route.fulfill(
            # Pass all fields from the response
            response=response,
            # override body
            body=live_event.strip()
        )
    page.route(
        "https://jupiter.tube/api/v1/video-channels/live/videos?isLive=true&skipCount=false&count=1&sort=-createdAt",
        handle_route
    )
