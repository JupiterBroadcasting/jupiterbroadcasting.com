from pytest import fixture
from playwright.sync_api import Page, expect


@fixture(autouse=True)
def setup(page: Page):
    page.goto("/hosts/")


def test_active_hosts_listed_first(page: Page):
    hosts = page.locator(".hosts-list")
    expect(hosts).to_contain_text("Chris Fisher")
    expect(hosts).not_to_contain_text("Jim Salter")


def test_former_hosts_section_at_bottom(page: Page):
    former = page.locator(".former-hosts-list")
    expect(former.locator("h2")).to_have_text("Former Hosts")
    expect(former).to_contain_text("Jim Salter")
    expect(former).not_to_contain_text("Chris Fisher")
    assert page.locator(".hosts-list ~ .former-hosts-list").count() == 1


def test_hidden_people_not_listed(page: Page):
    expect(page.locator("main, #wrapper")).not_to_contain_text("Friends of Jupiter Broadcasting")
