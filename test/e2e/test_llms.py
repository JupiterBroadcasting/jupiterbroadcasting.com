"""E2E checks for the llms.txt machinery against the built site.

Validates the llmstxt.org v2 contract:
  - /llms.txt exists at root with spec-conformant structure
  - /llms-full.txt exists
  - per-show llms.txt exists under each show path
  - pages have markdown twins at <url>index.md
  - HTML pages advertise discovery links (describedby / alternate)
"""
import re

from playwright.sync_api import Page


def _body(page: Page, url: str) -> str:
    resp = page.goto(url)
    assert resp is not None and resp.ok, f"{url} -> {resp.status if resp else 'no response'}"
    # served as a text file; playwright wraps it in <html><body><pre>
    return page.content()


def test_root_llms_txt(page: Page):
    body = _body(page, "/llms.txt")
    assert "Jupiter Broadcasting" in body
    assert "## Shows" in body
    assert "/show/linux-unplugged/llms.txt" in body


def test_llms_full_txt(page: Page):
    body = _body(page, "/llms-full.txt")
    assert "Membership" in body


def test_per_show_llms_and_markdown_twins(page: Page):
    body = _body(page, "/show/linux-unplugged/llms.txt")
    assert "## Episodes" in body
    m = re.search(r"\]\((https?://[^)]+/show/linux-unplugged/\d+/index\.md)\)", body)
    assert m, "episode entries must link to markdown twins"
    # fetch the twin relative to the base url (tests run with baseURL "/")
    twin = m.group(1).replace("https://www.jupiterbroadcasting.com", "")
    body = _body(page, twin)
    assert "Episode Links" in body or "URL:" in body


def test_discovery_links_on_html_pages(page: Page):
    page.goto("/")
    page.locator('link[rel="describedby"][href="/llms.txt"]').wait_for()
    page.goto("/show/linux-unplugged/")
    page.locator('link[rel="alternate"][type="text/markdown"]').wait_for()
