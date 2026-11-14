import re
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
    expect(former).to_contain_text("Alan Pope")
    expect(former).not_to_contain_text("Chris Fisher")
    assert page.locator(".hosts-list ~ .former-hosts-list").count() == 1


def test_former_hosts_title_spaced_from_cards(page: Page):
    former = page.locator(".former-hosts-list")
    title = former.locator("h2").bounding_box()
    first_card = former.locator(".column").first.locator("> *").first.bounding_box()
    assert first_card["y"] - (title["y"] + title["height"]) >= 8


def test_rule_separates_active_and_former_hosts(page: Page):
    rule = page.locator(".former-hosts-list hr").bounding_box()
    last_active = page.locator(".hosts-list .column").last.bounding_box()
    title = page.locator(".former-hosts-list h2").bounding_box()
    assert last_active["y"] + last_active["height"] <= rule["y"] < title["y"]


def test_hidden_people_not_listed(page: Page):
    expect(page.locator("main, #wrapper")).not_to_contain_text("Friends of Jupiter Broadcasting")


def test_former_hosts_paginated_and_links_jump_to_them(page: Page):
    """
    Former hosts are paginated; page links land on the Former Hosts heading, and active hosts stay on every page
    """
    pagination = page.locator('.former-hosts-list [aria-label="pagination"]')
    expect(pagination.locator(".pagination-link", has_text=re.compile(r"^\s*2\s*$"))).to_have_attribute(
        "href", re.compile(r"/hosts/page/2/#former-hosts$")
    )
    page.goto("/hosts/page/2/#former-hosts")
    expect(page.locator(".hosts-list")).to_contain_text("Chris Fisher")
    expect(page.locator(".former-hosts-list")).to_contain_text("Jim Salter")
    expect(page.locator(".former-hosts-list")).not_to_contain_text("Alan Pope")
