from pathlib import Path
from playwright.sync_api import Page, FrameLocator, Locator


def test_contact_screenshot(page: Page, screenshot_dir: Path):
    page.goto("/contact", wait_until="networkidle")
    page.screenshot(path=f"{screenshot_dir}/contact.png", full_page=True)

def test_submit_button_visible(page: Page, screenshot_dir: Path):
    page.goto("/contact")
    contact_form: FrameLocator = page.frame_locator('#contact-frame')
    submit_button: Locator = contact_form.locator("#saveForm")

    submit_button.click()
    page.wait_for_load_state("networkidle")

    # Scroll to the top (Page is current about 1400px)
    page.locator("h1").scroll_into_view_if_needed()

    frame_height: float = float(page.locator("#contact-frame").get_attribute("height")) + page.locator(selector="#contact-frame").bounding_box().get("y")

    button_location: dict = submit_button.bounding_box()
    if button_location is None:
        assert False, "Submit Button is hidden"
    button_bottom: float = button_location.get("y") + button_location.get("height")

    page.screenshot(path=f"{screenshot_dir}/contact_errors.png", full_page=True)
    assert button_bottom <= frame_height, "Form content is running off the iframe"
