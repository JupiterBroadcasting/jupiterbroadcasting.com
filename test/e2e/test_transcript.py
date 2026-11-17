import re

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
    expect(chris).to_contain_text("weekly Linux talk show. My name is Chris.")
    paras = page.locator(".transcript-para")
    expect(paras.nth(3).locator(".transcript-text")).to_have_text(re.compile(r"^Hello, gentlemen\..*time-appropriate greetings to that virtual lug\.$"))
    expect(paras.nth(4).locator(".transcript-time")).to_have_text("0:45")
    expect(paras.nth(4).locator(".transcript-speaker")).to_have_text("Chris")


def test_transcript_text_is_plain_text(page: Page):
    page.goto(LUP)
    expect(page.locator(".transcript-text a, .transcript-text v")).to_have_count(0)
    assert "<v " not in page.locator(".transcript-body").inner_html()


def test_transcript_source_link_points_at_vtt(page: Page):
    page.goto(LUP)
    expect(page.locator("a.transcript-source")).to_have_attribute("href", "https://feeds.jupiterbroadcasting.com/transcripts/lup/b13bcff0-5d43-46c9-af4e-b21fd70d4c88.vtt")


def test_srt_transcript_has_no_speaker(page: Page):
    page.goto("/show/this-week-in-bitcoin/129/")
    page.locator("details.transcript summary").click()
    first = page.locator(".transcript-para").first
    expect(first.locator(".transcript-time")).to_have_text("0:00")
    expect(first.locator(".transcript-text")).to_contain_text("Welcome in to This Week in Bitcoin, episode 129.")
    expect(page.locator(".transcript-speaker")).to_have_count(0)


def test_unknown_speaker_is_not_shown(page: Page):
    page.goto("/show/the-launch/90/")
    page.locator("details.transcript summary").click()
    expect(page.locator(".transcript-body")).not_to_contain_text("Unknown")
    expect(page.locator(".transcript-para").first.locator(".transcript-text")).to_contain_text("Streaming from the beautiful Pacific Northwest")


def test_no_transcript_block_without_transcripts(page: Page):
    page.goto("/show/linux-unplugged/434/")
    expect(page.locator("details.transcript")).to_have_count(0)


def test_no_transcript_block_for_text_only_transcripts(page: Page):
    page.goto("/show/jupiter-extras/94/")
    expect(page.locator("details.transcript")).to_have_count(0)
    expect(page.locator("p.transcript-unavailable")).to_have_count(0)


def test_transcript_is_downweighted_and_labels_are_not_indexed(page: Page):
    page.goto(LUP)
    expect(page.locator(".transcript-body")).to_have_attribute("data-pagefind-weight", "0.2")
    labels = page.locator(".transcript-time, .transcript-speaker")
    for i in range(labels.count()):
        expect(labels.nth(i)).to_have_attribute("data-pagefind-ignore", "")


def test_cue_text_has_no_markup_children(page: Page):
    page.goto(LUP)
    expect(page.locator(".transcript-text > *")).to_have_count(0)
