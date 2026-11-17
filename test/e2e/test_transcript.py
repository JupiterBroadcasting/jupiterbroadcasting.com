from playwright.sync_api import Page, expect

LUP = "/show/linux-unplugged/691/"


def test_vtt_transcript_is_collapsed_by_default(page: Page):
    page.goto(LUP)
    details = page.locator("details.transcript")
    expect(details).to_have_count(1)
    expect(details).not_to_have_attribute("open", "")
    expect(details.locator("summary")).to_have_text("Transcript")
    expect(details.locator(".transcript-body")).to_be_hidden()


def test_vtt_transcript_opens_with_speaker_time_and_text(page: Page):
    page.goto(LUP)
    page.locator("details.transcript summary").click()
    first = page.locator(".transcript-para").first
    expect(first.locator(".transcript-time")).to_have_text("0:11")
    expect(first.locator(".transcript-speaker")).to_have_text("Chris")
    expect(first.locator(".transcript-text")).to_contain_text("welcome back to your weekly Linux talk show")


def test_transcript_groups_cues_into_paragraphs(page: Page):
    page.goto(LUP)
    page.locator("details.transcript summary").click()
    chris = page.locator(".transcript-para").first.locator(".transcript-text")
    expect(chris).to_contain_text("My name is Chris")
    assert page.locator(".transcript-para").count() < 800


def test_transcript_text_is_plain_text(page: Page):
    page.goto(LUP)
    expect(page.locator(".transcript-text a, .transcript-text v")).to_have_count(0)
    assert "<v " not in page.locator(".transcript-body").inner_html()


def test_transcript_source_link_points_at_vtt(page: Page):
    page.goto(LUP)
    expect(page.locator("a.transcript-source")).to_have_attribute("href", "https://feeds.jupiterbroadcasting.com/transcripts/lup/b13bcff0-5d43-46c9-af4e-b21fd70d4c88.vtt")
