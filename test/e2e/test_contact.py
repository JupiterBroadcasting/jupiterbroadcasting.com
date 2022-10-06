from pytest import mark
from pathlib import Path
from playwright.sync_api import Page, expect


def test_contact_screenshot(page: Page, screenshot_dir: Path):
    page.goto("/contact")
    page.pause()
    page.screenshot(path=f"{screenshot_dir}/contact.png", full_page=True)

@mark.skip(reason="Not finished implementing")
def test_submit_button_visible(page: Page, screenshot_dir: Path):
    page.goto("/contact")
    contact_form: FrameLocator = page.frame_locator('#contact-frame')
    submit_button: Locator = contact_form.locator("#saveForm")

    submit_button.click()
    page.wait_for_load_state("networkidle")

    frame_height: int = int(page.get_attribute(selector="#contact-frame", name="height"))

    # Bounding Box is relative to view port, making this test invalid.
    # Need to find a way to get the bottom of the submit button in
    # pixels on the form to check if it is greater than the size of
    # the iframe
    button_location: dict = submit_button.bounding_box()
    if button_location is None:
        assert False, "Submit Button is hidden"
    button_bottom: float = button_location.get("y") + button_location.get("height")

    assert form_height <= frame_height, "Form content is running off the iframe"
    page.screenshot(path=f"{screenshot_dir}/contact_errors.png")
