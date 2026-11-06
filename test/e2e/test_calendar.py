from pytest import fixture, mark
from playwright.sync_api import Page, expect


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    # Keep Google Calendar out of the test: only the iframe src (our markup) is asserted.
    page.route("**/calendar/embed*", lambda route: route.abort())
    page.goto("/calendar")


@mark.browser_context_args(timezone_id="Asia/Tokyo")
def test_calendar_default_timezone(page: Page):
    """
    Ensure the calendar iframe defaults to the browser's timezone
    """
    iframe = page.locator("iframe")
    calendar_base = iframe.get_attribute("data-src")
    expect(iframe).to_have_attribute("src", calendar_base + "&ctz=Asia%2FTokyo")


def test_calendar_timezone(page: Page):
    """
    Ensure choosing a timezone in the dropdown updates the calendar iframe src
    """
    iframe = page.locator("iframe")
    calendar_base = iframe.get_attribute("data-src")

    page.locator("select#ctz").select_option("Europe/London")
    expect(iframe).to_have_attribute("src", calendar_base + "&ctz=Europe/London")

    page.locator("select#ctz").select_option("Pacific/Auckland")
    expect(iframe).to_have_attribute("src", calendar_base + "&ctz=Pacific/Auckland")


def test_calendar_timezone_placeholder(page: Page):
    """
    Ensure re-selecting the placeholder option leaves the current timezone in place
    """
    iframe = page.locator("iframe")
    calendar_base = iframe.get_attribute("data-src")

    page.locator("select#ctz").select_option("Europe/London")
    page.locator("select#ctz").select_option("none")
    expect(iframe).to_have_attribute("src", calendar_base + "&ctz=Europe/London")
