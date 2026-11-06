import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Page, expect

from episode_data import CONTENT, CONTENT_SHOW, Episode, episodes_by_date

SITE_PAGES = ["/", "/show/", "/archive/", "/membership/", "/live/", "/community/", "/sponsors/", "/contact/", "/calendar/", "/people/"]
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
OGIMAGE = re.search(r'^ogimage\s*=\s*"([^"]+)"', (CONTENT.parent / "config/_default/params.toml").read_text(), re.M).group(1)

EPISODES = {s.name: episodes_by_date(s) for s in sorted(CONTENT_SHOW.iterdir()) if (s / "_index.md").exists()}
ALL_EPISODES = [e for eps in EPISODES.values() for e in eps]


def _path(url: str) -> str:
    return re.sub(r"^https?://[^/]+", "", url)


def _published(episode: Episode) -> datetime:
    parsed = datetime.fromisoformat(episode.data["date"])
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _xml(api: APIRequestContext, path: str) -> ET.Element:
    response = api.get(path)
    assert response.status == 200, f"{path} returned {response.status}"
    assert "xml" in response.headers["content-type"], response.headers["content-type"]
    return ET.fromstring(response.body())


def test_sitemap(api_request_context: APIRequestContext):
    """
    sitemap.xml lists the core pages, every show, and every episode
    """
    locs = {_path(loc.text) for loc in _xml(api_request_context, "/sitemap.xml").iterfind("s:url/s:loc", SITEMAP_NS)}
    expected = set(SITE_PAGES) | {f"/show/{s}/" for s in EPISODES} | {e.url for e in ALL_EPISODES}
    missing = sorted(expected - locs)
    assert not missing, f"{len(missing)} pages missing from sitemap.xml, e.g. {missing[:5]}"


def test_rss_feed(api_request_context: APIRequestContext):
    """
    /index.xml is RSS 2.0 with complete items, newest first, starting at the newest episode
    """
    rss = _xml(api_request_context, "/index.xml")
    assert rss.tag == "rss" and rss.get("version") == "2.0"
    items = rss.findall("channel/item")
    assert items, "feed has no items"
    for item in items:
        assert item.findtext("title") and item.findtext("link") and item.findtext("pubDate"), ET.tostring(item)[:200]
    dates = [parsedate_to_datetime(item.findtext("pubDate")) for item in items]
    assert dates == sorted(dates, reverse=True), "items must be newest first"
    newest = max(_published(e) for e in ALL_EPISODES)
    newest_urls = {e.url for e in ALL_EPISODES if _published(e) == newest}
    assert _path(items[0].findtext("link")) in newest_urls, "first item should be the newest episode"


def _show_header_image(slug: str) -> str:
    return re.search(r'^header_image\s*=\s*"([^"]+)"', (CONTENT_SHOW / slug / "_index.md").read_text(), re.M).group(1)


MISSING_OGIMAGE = mark.xfail(
    strict=True,
    reason=f"ogimage in config/_default/params.toml is {OGIMAGE}, which doesn't exist (404 in production too)",
)


def _meta_params() -> list:
    lup = EPISODES["linux-unplugged"][-1]
    return [
        param("/", None, id="home", marks=MISSING_OGIMAGE),
        param("/show/linux-unplugged/", _show_header_image("linux-unplugged"), id="show"),
        param(lup.url, lup.data.get("header_image"), id="episode"),
        param("/hosts/chris/", None, id="host", marks=MISSING_OGIMAGE),
        param("/community/irc/", None, id="community", marks=MISSING_OGIMAGE),
    ]


@mark.only_browser("chromium")
@mark.parametrize("path, image", _meta_params())
def test_social_meta(page: Page, api_request_context: APIRequestContext, path: str, image: str | None):
    """
    Open Graph / Twitter tags match the page: same title, canonical URL, and the header image (or the site default)
    """
    page.goto(path, wait_until="domcontentloaded")
    title = page.title()
    head = page.locator("head")
    for selector in ('meta[property="og:title"]', 'meta[name="twitter:title"]'):
        expect(head.locator(selector)).to_have_attribute("content", title)
    for selector in ('meta[property="og:url"]', 'meta[name="twitter:url"]', 'link[rel="canonical"]'):
        attr = "href" if selector.startswith("link") else "content"
        expect(head.locator(selector)).to_have_attribute(attr, re.compile(rf"^(https?://[^/]+)?{re.escape(path)}$"))
    expect(head.locator('meta[property="og:description"]')).to_have_attribute("content", re.compile(r"\S"))

    og_image = head.locator('meta[property="og:image"]').get_attribute("content")
    expect(head.locator('meta[name="twitter:image"]')).to_have_attribute("content", og_image)
    if image:
        assert _path(og_image) == _path(image), "og:image should be the page's header_image"
    else:
        assert _path(og_image) == OGIMAGE, "pages without a header_image use the site default"
        response = api_request_context.get(OGIMAGE)
        assert response.status == 200, f"default og:image {OGIMAGE} returned {response.status}"
