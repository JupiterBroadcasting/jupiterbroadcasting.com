from playwright.sync_api import Page, expect

"""
Checking for broken tag links with spaces in them
"""
def test_tag_broken_link_spaces(page: Page):
    page.goto("/show/linux-unplugged/489/")
    page.locator(".tag > a", has_text="linux unplugged").click()
    expect(page.locator(".title", has_text="Tag: linux unplugged")).to_be_visible()
