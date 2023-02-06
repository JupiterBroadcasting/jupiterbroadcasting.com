from pathlib import Path
from pytest import fixture
from playwright.sync_api import Page, FrameLocator, Locator


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/contact")


def test_submit_button_visible(page: Page, screenshot_dir: Path):
    """
    This test ensures that the "Submit" button at the bottom of the contact form is always visible to the user, even if they forget the fill in the fields. This
    test also saves a screenshot of the contact page after the form validation errors have been generated for manual review if needed.

    Steps:
      1. Go to contact page
      2. Click "Submit" button without filling out any data
      3. Get the height of the iframe (defined as an html attribute) and adds it to the distance from the top of the screen to the top of the iframe
      4. Measure the height of the top of the screen to the bottom of the "Submit" button
      5. Pass if the distance from the bottom of the iframe is greater than the distance to the bottom of the button in the iframe (ie. the button can be seen)
    """
    contact_form: FrameLocator = page.frame_locator('#contact-frame')
    submit_button: Locator = contact_form.locator("#saveForm")

    submit_button.click()
    page.wait_for_load_state("networkidle")

    page.locator("h1").scroll_into_view_if_needed()

    # This test assumes the iframe will always be rendered, if the test fails here, the iframe is missing
    frame_height: float = float(page.locator("#contact-frame").get_attribute("height")) + \
        page.locator(selector="#contact-frame").bounding_box().get("y")

    # This is just a precautionary measure to ensure the submit button is on the screen it'll return None if it's not,
    # and since here are more places use the value from the bounding_box's return ensuring it's not None
    button_location: dict = submit_button.bounding_box()
    if button_location is None:
        assert False, "Submit Button is hidden"
    button_bottom: float = button_location.get("y") + button_location.get("height")

    assert button_bottom <= frame_height, "Form content is running off the iframe"
