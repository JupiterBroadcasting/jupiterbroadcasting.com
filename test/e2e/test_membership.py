import re
from pathlib import Path

from pytest import fixture, mark
from playwright.sync_api import Page, expect

MEMBERSHIP_MD = Path(__file__).parents[2] / "content/membership/index.md"
MEMBERSHIP_LINK = re.compile(
    r"\[([^\]]+)\]\((https://(?:jupitersignal\.memberful\.com|www\.jupiter\.party)/[^)]*)\)"
)
MEMBERSHIP_LINKS = MEMBERSHIP_LINK.findall(MEMBERSHIP_MD.read_text(encoding="utf-8"))


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/membership/")


def test_membership_links_found():
    """
    Guard against the regex silently matching nothing
    """
    assert MEMBERSHIP_LINKS


@mark.parametrize("text,href", MEMBERSHIP_LINKS, ids=[href for _, href in MEMBERSHIP_LINKS])
def test_membership_links(page: Page, text: str, href: str):
    """
    Ensure every membership link in content/membership/index.md renders with the same href and text
    """
    link = page.locator(f'a[href="{href}"]')
    expect(link).to_have_count(1)
    expect(link).to_be_visible()
    expect(link).to_have_text(text)
