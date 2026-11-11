from playwright.sync_api import Page, expect

LAS_MP4 = "http://201402.jb-dl.cdn.scaleengine.net/las/2014/linuxactionshowep300-432p.mp4"


def test_podverse_player_when_show_has_podverse_id(page: Page):
    page.goto("/show/coder-radio/343/")
    expect(page.locator("#pv-embed-player")).to_have_count(1)


def test_native_audio_player_without_podverse_id(page: Page):
    page.goto("/show/techsnap/191/")
    expect(page.locator("#pv-embed-player")).to_have_count(0)
    expect(page.locator("audio.episode-player source")).to_have_count(1)


def test_youtube_player_without_audio(page: Page):
    page.goto("/show/linux-action-show/300/")
    expect(page.locator("#pv-embed-player")).to_have_count(0)
    expect(page.locator("audio.episode-player")).to_have_count(0)
    expect(page.locator(".episode-player iframe")).to_have_attribute(
        "src", "https://www.youtube-nocookie.com/embed/ktySRTnT2ZE")


def test_video_only_episode_has_no_mp3_link(page: Page):
    page.goto("/show/linux-action-show/300/")
    links = page.locator(".download-links")
    expect(links.get_by_role("link", name="MP3", exact=True)).to_have_count(0)
    expect(links.get_by_role("link", name="Video", exact=True)).to_have_attribute("href", LAS_MP4)


def test_no_player_or_mp3_link_without_media(page: Page):
    page.goto("/show/linux-action-show/13/")
    expect(page.locator("#pv-embed-player, .episode-player")).to_have_count(0)
    expect(page.locator(".download-links").get_by_role("link", name="MP3", exact=True)).to_have_count(0)
