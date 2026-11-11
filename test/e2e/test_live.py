import re
from pathlib import Path

from pytest import fixture
from playwright.sync_api import Page, Route, expect

CONFIG: str = (Path(__file__).parents[2] / "config.toml").read_text()
VIDEO_URL: str = re.search(r'^\s*video_url\s*=\s*"([^"]+)"', CONFIG, re.M).group(1)
AUDIO_URL: str = re.search(r'^\s*audio_url\s*=\s*"([^"]+)"', CONFIG, re.M).group(1)
STREAM_HOST: str = re.match(r"https?://[^/]+", VIDEO_URL).group(0)

# a live (no ENDLIST) media playlist; segment requests are left pending so hls.js never sees a segment error
LIVE_PLAYLIST: str = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:6\n#EXT-X-MEDIA-SEQUENCE:0\n#EXTINF:6.0,\nseg0.ts\n"

# hls.js retries a failed manifest before declaring the stream offline
OFFLINE_TIMEOUT_MS: int = 20_000


class StreamStub:
    """
    Answers every request to the live stream host, so tests never touch the real stream
    """

    def __init__(self) -> None:
        self.live = False
        self.playlist_requests = 0

    def handle(self, route: Route) -> None:
        if not route.request.url.startswith(VIDEO_URL):
            return  # segments: leave pending
        self.playlist_requests += 1
        if self.live:
            route.fulfill(status=200, content_type="application/vnd.apple.mpegurl", body=LIVE_PLAYLIST)
        else:
            route.abort()


@fixture
def stream(page: Page) -> StreamStub:
    stub = StreamStub()
    page.route(f"{STREAM_HOST}/**", stub.handle)
    page.route(f"{AUDIO_URL.split('?')[0]}*", lambda route: route.abort())
    return stub


def test_live_offline_overlay(page: Page, stream: StreamStub):
    """
    When the stream can't be reached, the "Currently Off Air" overlay is shown
    """
    page.goto("/live/")
    overlay = page.locator("#stream-offline")
    expect(overlay).to_have_class(re.compile(r"\bis-visible\b"), timeout=OFFLINE_TIMEOUT_MS)
    expect(overlay).to_contain_text("Currently Off Air")
    expect(overlay.locator('a[href="/calendar/"]')).to_be_visible()


def test_live_online_hides_overlay(page: Page, stream: StreamStub):
    """
    "Try Again" reconnects, and once the stream answers the off-air overlay is hidden
    """
    page.goto("/live/")
    overlay = page.locator("#stream-offline")
    expect(overlay).to_have_class(re.compile(r"\bis-visible\b"), timeout=OFFLINE_TIMEOUT_MS)

    stream.live = True
    requests_before = stream.playlist_requests
    page.locator("#retry-button").click()

    expect(overlay).not_to_have_class(re.compile(r"\bis-visible\b"), timeout=OFFLINE_TIMEOUT_MS)
    assert stream.playlist_requests > requests_before


def test_live_toggle_audio_video(page: Page, stream: StreamStub):
    """
    The toggle button swaps between the video and audio players and relabels itself. It's found by role and
    accessible name, so this is also what a screen reader user hears and activates
    """
    page.goto("/live/")
    audio_player = page.locator("#audio-player")
    video_wrapper = page.locator("#video-player .video-wrapper")

    expect(audio_player).to_be_hidden()
    expect(video_wrapper).to_be_visible()

    page.get_by_role("button", name="Switch to Audio", exact=True).click()
    expect(audio_player).to_be_visible()
    expect(video_wrapper).to_be_hidden()

    page.get_by_role("button", name="Switch to Video", exact=True).click()
    expect(audio_player).to_be_hidden()
    expect(video_wrapper).to_be_visible()
    expect(page.get_by_role("button", name="Switch to Audio", exact=True)).to_be_visible()
