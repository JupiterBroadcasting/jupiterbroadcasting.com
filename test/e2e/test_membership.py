import tomllib
from pathlib import Path

from pytest import fixture, param, mark
from playwright.sync_api import APIRequestContext, Page, expect

MEMBERSHIP_MD = Path(__file__).parents[2] / "content/membership/index.md"
MEMBERSHIP = tomllib.loads(MEMBERSHIP_MD.read_text(encoding="utf-8").split("+++")[1])
PLANS = [plan for group in MEMBERSHIP["plan_groups"] for plan in group["plans"]]
PLAN_PARAMS = [param(p["name"], p["url"], id=p["url"]) for p in PLANS]


@fixture
def membership(page: Page) -> Page:
    page.goto("/membership/")
    return page


def test_membership_plans_found():
    """
    Guard against the front matter silently losing its plans
    """
    assert PLANS and MEMBERSHIP["perks"]


@mark.parametrize("text,href", PLAN_PARAMS)
def test_membership_links(membership: Page, text: str, href: str):
    """
    Ensure every plan in content/membership/index.md front matter renders with the same href and text
    """
    link = membership.locator(f'a[href="{href}"]')
    expect(link).to_have_count(1)
    expect(link).to_be_visible()
    expect(link).to_have_text(text)


@mark.parametrize("perk", [param(p, id=p["show"]) for p in MEMBERSHIP["perks"]])
def test_membership_perks(membership: Page, perk: dict):
    """
    Each show's perks are listed under a heading linking to the show
    """
    heading = membership.locator("h4", has=membership.locator(f'a[href="/show/{perk["show"]}/"]'))
    expect(heading).to_have_count(1)
    items = heading.locator("xpath=following-sibling::ul[1]/li")
    expect(items).to_have_count(len(perk["items"]))
    for item, li in zip(perk["items"], items.all()):
        expect(li).to_contain_text(item["name"])


def test_membership_markdown(api_request_context: APIRequestContext):
    """
    index.md carries every plan and perk from the front matter, not raw shortcodes
    """
    text = api_request_context.get("/membership/index.md").text()
    for plan in PLANS:
        assert f"- [{plan['name']}]({plan['url']})" in text, plan["name"]
    for perk in MEMBERSHIP["perks"]:
        assert f"/show/{perk['show']}/)" in text, perk["show"]
        for item in perk["items"]:
            assert f"- {item['name']}" in text, item["name"]
    assert "{{" not in text and "+++" not in text, "template or front matter leaked"
