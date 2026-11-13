import html
import tomllib
import re
import unicodedata
from functools import cache
from pathlib import Path

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Page

from episode_data import CONTENT_SHOW, META_FILES, load_episode, sample_episodes

HOST = r"(?:https?://[^/\"]+)?"
EMOJI_SLUGS = Path(__file__).parents[2] / "data" / "emoji_slugs.toml"
SLUGS: dict[str, str] = tomllib.loads(EMOJI_SLUGS.read_text())

HASH = mark.xfail(reason="partials/episode/tags.html leaves '#' unescaped, so the link ends at a URL fragment")
# (id, tag, episode carrying it, marks for the link from that episode page); episodes are in EXTRA_EPISODES
CASES: list[tuple[str, str, str, list]] = [
    ("space", "coder radio", "/show/coder-radio/451/", []),
    ("apostrophe", "apple's plan to crack small business", "/show/coder-radio/443/", []),
    ("ampersand", "shearman & sterling", "/show/linux-action-news/129/", []),
    ("space-hyphen", "sudo rm -rf", "/show/linux-unplugged/565/", []),
    ("plus", "disney+ drm", "/show/linux-action-news/129/", []),
    ("dot", "ruby vs. c++", "/show/coder-radio/451/", []),
    ("curly-quote", "epic\u2019s appeal", "/show/coder-radio/451/", []),
    ("hash-leading", "#freefortnite", "/show/coder-radio/451/", [HASH]),
    ("hash-trailing", "c#", "/show/coder-radio/343/", [HASH]),
    ("emoji", "🤦", "/show/linux-unplugged/565/", []),
    ("emoji-only", "🦒", "/show/linux-unplugged/604/", []),
    ("emoji-only-multi", "🤟❄️⚖️", "/show/linux-unplugged/604/", []),
]


@cache
def _tags_index(api: APIRequestContext) -> dict[str, str]:
    """
    tag title -> href from /tags/
    """
    response = api.get("/tags/")
    assert response.ok, f"/tags/ returned {response.status}"
    return {
        html.unescape(title): html.unescape(href)
        for href, title in re.findall(r"<a href='([^']+)'>(.*?) \(\d+\)</a>", response.text())
    }


def _tag_page_lists(api: APIRequestContext, href: str, urls: list[str]) -> list[str]:
    response = api.get(href)
    assert response.status == 200, f"{href} returned {response.status}"
    text = response.text()
    return [url for url in urls if not re.search(rf'href="{HOST}{re.escape(url)}"', text)]


def test_cases_are_sample_episodes():
    sample = {e.url for e in sample_episodes()}
    assert [episode for _, _, episode, _ in CASES if episode not in sample] == []


def test_tags_without_text_have_a_slug():
    """
    An emoji-only tag has an empty URL slug, so Hugo writes its term page to /tags/ and overwrites the index
    (Issue #516). data/emoji_slugs.toml gives it a slug of its own.
    """
    tags = {
        tag
        for path in CONTENT_SHOW.glob("*/*.md")
        if path.name not in META_FILES
        for tag in load_episode(path).data.get("tags") or []
    }
    missing = [
        tag
        for tag in sorted(tags)
        if any(unicodedata.category(c) == "So" for c in tag)
        and not re.search(r"[^\W_]", tag)
        and tag not in SLUGS
    ]
    assert not missing, f"add a line to data/emoji_slugs.toml for: {missing}"


@mark.parametrize("tag,episode", [param(tag, episode, id=id) for id, tag, episode, _ in CASES])
def test_tags_index_entry(api_request_context: APIRequestContext, tag: str, episode: str):
    """
    /tags/ lists the tag, and its link leads to a tag page listing the episode
    """
    index = _tags_index(api_request_context)
    assert tag in index, f"{tag!r} missing from /tags/"
    missing = _tag_page_lists(api_request_context, index[tag], [episode])
    assert not missing, f"{index[tag]} doesn't list {episode}"


@mark.only_browser("chromium")
@mark.parametrize("tag,episode", [param(tag, episode, id=id, marks=marks) for id, tag, episode, marks in CASES])
def test_tag_link_from_episode(page: Page, api_request_context: APIRequestContext, tag: str, episode: str):
    """
    The tag link on an episode page leads to a tag page that lists the episode. An emoji-only tag links to
    /tags/<slug>/ from data/emoji_slugs.toml, not /tags/ (Issue #516).
    """
    page.goto(episode, wait_until="domcontentloaded")
    links = page.locator(".tags .tag a").filter(has_text=re.compile(rf"^\s*{re.escape(tag)}\s*$"))
    assert links.count() == 1, f"{episode} should show tag {tag!r} once"
    href = links.first.get_attribute("href")
    if tag in SLUGS:
        assert href == f"/tags/{SLUGS[tag]}/"
    missing = _tag_page_lists(api_request_context, href, [episode])
    assert not missing, f"{href} doesn't list {episode}"


@mark.only_browser("chromium")
def test_tag_page_heading(page: Page, api_request_context: APIRequestContext):
    """
    A tag page titles itself with the tag and lists the episodes carrying it as cards
    """
    episodes = ["/show/coder-radio/451/", "/show/linux-unplugged/565/"]
    page.goto("/tags/microsoft/")
    assert page.locator("h1.title").inner_text().split() == ["Tag:", "microsoft"]
    assert page.locator(".card-episode").count() >= len(episodes)
    missing = _tag_page_lists(api_request_context, "/tags/microsoft/", episodes)
    assert not missing, f"/tags/microsoft/ doesn't list {missing}"
