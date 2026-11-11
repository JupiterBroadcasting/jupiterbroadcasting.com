import html
import re
import unicodedata
from collections import defaultdict
from functools import cache
from typing import Callable

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Page

from episode_data import CONTENT, CONTENT_SHOW, META_FILES, load_episode

HOST = r"(?:https?://[^/\"]+)?"


def _episodes_by_tag() -> dict[str, list[str]]:
    tags: dict[str, list[str]] = defaultdict(list)
    for path in sorted(CONTENT_SHOW.glob("*/*.md")):
        if path.name in META_FILES:
            continue
        episode = load_episode(path)
        for tag in episode.data.get("tags") or []:
            tags[tag].append(episode.url)
    return tags


EPISODES_BY_TAG = _episodes_by_tag()

DOUBLE_HYPHEN = mark.xfail(
    reason="partials/episode/tags.html builds the URL by hand (spaces to hyphens, then urlize), "
    "which leaves a double hyphen where Hugo 0.105's term permalink has one",
)
HASH = mark.xfail(reason="partials/episode/tags.html leaves '#' unescaped, so the link ends at a URL fragment")
# (category, matches, marks for /tags/ index test, marks for the link from an episode page)
CATEGORIES: list[tuple[str, Callable[[str], bool], list, list]] = [
    ("space", lambda t: re.fullmatch(r"[a-z0-9]+( [a-z0-9]+)+", t) is not None, [], []),
    ("apostrophe", lambda t: "'" in t, [], []),
    ("ampersand", lambda t: " & " in t, [], [DOUBLE_HYPHEN]),
    ("space-hyphen", lambda t: " -" in t, [], [DOUBLE_HYPHEN]),
    ("plus", lambda t: "+" in t and "#" not in t, [], []),
    ("hash", lambda t: "#" in t, [], [HASH]),
    ("dot", lambda t: "." in t, [], []),
    ("curly-quote", lambda t: any(c in "‘’“”" for c in t), [], []),
    ("emoji", lambda t: any(unicodedata.category(c) == "So" for c in t), [], []),
]


def _tag_params(marks_index: int) -> list:
    params = []
    for category in CATEGORIES:
        name, matches = category[:2]
        tag = next((t for t in sorted(EPISODES_BY_TAG) if matches(t)), None)
        if tag is not None:
            params.append(param(tag, id=name, marks=category[marks_index]))
    return params


INDEX_PARAMS = _tag_params(2)
LINK_PARAMS = _tag_params(3)


@cache
def _tags_index(api: APIRequestContext) -> dict[str, tuple[str, int]]:
    """
    tag title -> (href, count) from /tags/
    """
    response = api.get("/tags/")
    assert response.ok, f"/tags/ returned {response.status}"
    return {
        html.unescape(title): (html.unescape(href), int(count))
        for href, title, count in re.findall(
            r"<a href='([^']+)'>(.*?) \((\d+)\)</a>", response.text()
        )
    }


def _tag_page_lists(api: APIRequestContext, href: str, urls: list[str]) -> list[str]:
    response = api.get(href)
    assert response.status == 200, f"{href} returned {response.status}"
    text = response.text()
    return [url for url in urls if not re.search(rf'href="{HOST}{re.escape(url)}"', text)]


def test_tag_categories_found():
    """
    Every edge-case category still has a tag in content, so the parametrized tests below aren't silently empty
    """
    expected = {category[0] for category in CATEGORIES}
    found = {p.id for p in INDEX_PARAMS}
    assert found == expected, f"no tag in content for: {expected - found}"


def test_tags_without_text_have_a_term_file():
    """
    An emoji-only tag has an empty URL slug, so Hugo writes its term page to /tags/ and overwrites the index
    (Issue #516). content/tags/<tag>/_index.md gives it a slug of its own.
    """
    missing = [
        tag
        for tag in EPISODES_BY_TAG
        if any(unicodedata.category(c) == "So" for c in tag)
        and not re.search(r"[^\W_]", tag)
        and not (CONTENT / "tags" / tag / "_index.md").exists()
    ]
    assert not missing, f"add content/tags/<tag>/_index.md with a slug for: {missing}"


@mark.parametrize("tag", INDEX_PARAMS)
def test_tags_index_entry(api_request_context: APIRequestContext, tag: str):
    """
    /tags/ lists the tag with at least as many episodes as carry it in content, and its link
    leads to a tag page listing those episodes
    """
    index = _tags_index(api_request_context)
    assert tag in index, f"{tag!r} missing from /tags/"
    href, count = index[tag]
    episodes = EPISODES_BY_TAG[tag]
    # tags differing only in spaces/hyphens share a page, so the count can be higher
    assert count >= len(episodes), f"/tags/ count {count} < {len(episodes)} episodes in content"
    missing = _tag_page_lists(api_request_context, href, episodes)
    assert not missing, f"episodes missing from {href}: {missing}"


@mark.only_browser("chromium")
@mark.parametrize("tag", LINK_PARAMS)
def test_tag_link_from_episode(page: Page, api_request_context: APIRequestContext, tag: str):
    """
    The tag link on an episode page leads to a tag page that lists the episode
    """
    episode = EPISODES_BY_TAG[tag][0]
    page.goto(episode, wait_until="domcontentloaded")
    links = page.locator(".tags .tag a").filter(has_text=re.compile(rf"^\s*{re.escape(tag)}\s*$"))
    assert links.count() == 1, f"{episode} should show tag {tag!r} once"
    href = links.first.get_attribute("href")
    missing = _tag_page_lists(api_request_context, href, [episode])
    assert not missing, f"{href} doesn't list {episode}"


@mark.only_browser("chromium")
def test_tag_page_heading(page: Page):
    """
    A tag page titles itself with the tag and lists every episode carrying it as a card
    """
    tag, episodes = next((t, e) for t, e in sorted(EPISODES_BY_TAG.items()) if re.fullmatch(r"[a-z]+", t) and len(e) > 1)
    page.goto(f"/tags/{tag}/")
    assert page.locator("h1.title").inner_text().split() == ["Tag:", tag]
    assert page.locator(".card-episode").count() >= len(episodes)
