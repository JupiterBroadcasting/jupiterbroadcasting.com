"""
JSON twins of shows and episodes: /show/<slug>/show.json and /show/<slug>/<NNNN>.json (schema in docs/json-schema.md).

Expected values come from content/ so the tests hold for any content snapshot.
Links may be absolute (production) or site-relative (CI builds with baseURL "/").
"""
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from pytest import mark, param
from playwright.sync_api import APIRequestContext

from episode_data import (
    CONTENT,
    CONTENT_SHOW,
    Episode,
    _published,
    episodes_by_date,
    load_episode,
    person_type,
    sample_episodes,
    sponsor_exists,
)

HOST = r"(?:https?://[^/)\s]+)?"


@dataclass(frozen=True)
class Show:
    slug: str
    title: str
    episodes: tuple[Episode, ...]  # oldest first


def _toml_field(path: Path, key: str) -> str:
    return re.search(rf'^{key}\s*=\s*"(.*)"\s*$', path.read_text(), re.M).group(1)


SHOWS: list[Show] = [
    Show(
        slug=d.name,
        title=_toml_field(d / "_index.md", "title"),
        episodes=tuple(e for e in episodes_by_date(d) if e.data.get("type") == "episode"),
    )
    for d in sorted(CONTENT_SHOW.iterdir())
    if (d / "_index.md").exists()
]
SHOW_PARAMS = [param(s, id=s.slug) for s in SHOWS]


def get_json(api: APIRequestContext, path: str) -> dict:
    response = api.get(path)
    assert response.status == 200, f"{path}: expected 200, got {response.status}"
    assert response.headers["content-type"].startswith("application/json"), (
        f"{path}: expected application/json, got {response.headers['content-type']}"
    )
    return response.json()


@mark.parametrize("show", SHOW_PARAMS)
def test_show_json(api_request_context: APIRequestContext, show: Show):
    """
    show.json carries the show facts, counts match content, and links to the other twins
    """
    base = f"/show/{show.slug}"
    data = get_json(api_request_context, f"{base}/show.json")
    newest = show.episodes[-1]

    assert find_nulls(data) == [], "null fields must be omitted at every depth"
    assert data["schema_version"] == 1
    assert data["type"] == "show"
    assert data["slug"] == show.slug
    assert data["name"] == show.title
    assert data["episode_count"] == len(show.episodes)
    assert data["latest_episode"]["episode"] == int(newest.number)
    assert re.fullmatch(rf"{HOST}{re.escape(newest.url)}", data["latest_episode"]["url"])
    assert "json_url" not in data, "a show's own JSON URL is the URL it was fetched from"
    assert re.fullmatch(rf"{HOST}{base}/show\.md", data["markdown_url"])
    assert re.fullmatch(rf"{HOST}{base}/episodes\.json", data["episodes_url"])
    assert isinstance(data["hosts"], list) and data["hosts"], "show has hosts in front matter"
    for host in data["hosts"]:
        resolved = person_type(host["slug"]) is not None
        assert ("url" in host and bool(host.get("name"))) == resolved, f"host {host} vs people page"
    numbers = [e.data["episode"] for e in show.episodes if isinstance(e.data["episode"], int)]
    special = [e for e in show.episodes if not isinstance(e.data["episode"], int)]
    assert data["numbered_episodes"]["first"] == min(numbers)
    assert data["numbered_episodes"]["last"] == max(numbers)
    assert data["numbered_episodes"].get("missing", []) == sorted(set(range(min(numbers), max(numbers) + 1)) - set(numbers))
    assert [s["episode"] for s in data["special_episodes"]] == [e.data["episode"] for e in special], "oldest first"
    for entry in data["special_episodes"][:1]:
        assert get_json(api_request_context, urlparse(entry["json_url"]).path)["episode"] == entry["episode"]
    assert "podverse_podcast_id" not in data
    assert data.get("podverse_url") == (f"https://podverse.fm/podcast/{podverse_id(show.slug)}" if podverse_id(show.slug) else None)
    assert isinstance(data["links"], dict) and all(isinstance(v, str) and v for v in data["links"].values())


# the-launch T-0: uppercase slug, non-numeric episode number
CORE_EPISODES: list[Episode] = list(
    {e.url: e for e in [*sample_episodes(), load_episode(CONTENT_SHOW / "the-launch" / "T-0.md")]}.values()
)
EPISODE_PARAMS = [param(e, id=e.url, marks=mark.episodes) for e in CORE_EPISODES]


def podverse_id(show_slug: str) -> str | None:
    match = re.search(r'^podverse_podcast_id\s*=\s*"(.*)"', (CONTENT_SHOW / show_slug / "_index.md").read_text(), re.M)
    return match.group(1) if match else None


def sponsor_link(shortname: str) -> str:
    return re.search(r"^link: *(\S+)", (CONTENT / "sponsors" / f"{shortname}.md").read_text(), re.M).group(1)


def strip_nulls(value):
    if isinstance(value, dict):
        return {k: strip_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [strip_nulls(v) for v in value]
    return value


def find_nulls(value, path: str = "") -> list[str]:
    if value is None:
        return [path]
    if isinstance(value, dict):
        return [n for k, v in value.items() for n in find_nulls(v, f"{path}.{k}")]
    if isinstance(value, list):
        return [n for i, v in enumerate(value) for n in find_nulls(v, f"{path}[{i}]")]
    return []


def episode_json_path(ep: Episode) -> str:
    return f"{ep.url.rstrip('/')}.json"


@mark.parametrize("ep", EPISODE_PARAMS)
def test_episode_json_core(api_request_context: APIRequestContext, ep: Episode):
    """
    Episode JSON carries the front matter facts, omits what the episode lacks, and links to its twins
    """
    d = ep.data
    data = get_json(api_request_context, episode_json_path(ep))

    assert data["schema_version"] == 1
    assert data["type"] == "episode"
    assert data["episode"] == d["episode"]
    assert data["title"] == d["title"]
    assert "guid" not in data
    assert data.get("description") == (d.get("description") or None)
    assert datetime.fromisoformat(data["date"]) == _published(d["date"])
    assert data["tags"] == (d.get("tags") or []), "tags must round-trip exactly (quotes, emoji, '+', '&')"
    assert data.get("youtube_url") == (d.get("youtube_link") or None)
    chapters = (d.get("podcast_chapters") or {}).get("chapters")
    assert data.get("chapters") == (strip_nulls(chapters) or None), "chapters is the bare list, nulls dropped"
    assert data.get("transcripts") == (strip_nulls(d.get("transcripts")) or None)

    if d.get("podcast_file"):
        assert data["audio"]["url"] == d["podcast_file"]
        assert data["audio"].get("bytes") == d.get("podcast_bytes")
        assert data["audio"].get("duration") == d.get("podcast_duration")
    else:
        assert "audio" not in data

    assert re.fullmatch(rf"{HOST}{re.escape(ep.url)}", data["url"])
    assert "json_url" not in data, "an episode's own JSON URL is the URL it was fetched from"
    assert re.fullmatch(rf"{HOST}{re.escape(ep.url.rstrip('/'))}\.md", data["markdown_url"])
    assert data["show"]["slug"] == ep.show
    assert re.fullmatch(rf"{HOST}/show/{ep.show}/show\.json", data["show"]["json_url"])
    assert re.fullmatch(rf"{HOST}/show/{ep.show}/show\.md", data["show"]["markdown_url"])
    assert re.fullmatch(rf"{HOST}/show/{ep.show}/llms\.txt", data["show"]["llms_url"])
    assert find_nulls(data) == [], "null fields must be omitted at every depth"

    assert "podverse_url" not in data, "podverse.fm episode pages use Podverse's own id, which the guid cannot give us"


@mark.parametrize("show", SHOW_PARAMS)
def test_show_latest_episode_json_resolves(api_request_context: APIRequestContext, show: Show):
    """
    The show's latest_episode.json_url leads to that episode's JSON
    """
    latest = get_json(api_request_context, f"/show/{show.slug}/show.json")["latest_episode"]
    episode = get_json(api_request_context, urlparse(latest["json_url"]).path)
    assert episode["type"] == "episode"
    assert episode["episode"] == latest["episode"]


@mark.parametrize("ep", EPISODE_PARAMS)
def test_episode_json_refs(api_request_context: APIRequestContext, ep: Episode):
    """
    Hosts, guests and sponsors keep front matter order and resolve to names and URLs; refs without a page keep only the id
    """
    data = get_json(api_request_context, episode_json_path(ep))

    for key in ("hosts", "guests"):
        assert [r["slug"] for r in data[key]] == (ep.data.get(key) or [])
        for ref in data[key]:
            resolved = person_type(ref["slug"]) is not None
            assert ("url" in ref and bool(ref.get("name"))) == resolved, f"{key} {ref} vs people page"

    assert [s["shortname"] for s in data["sponsors"]] == (ep.data.get("sponsors") or [])
    for sponsor in data["sponsors"]:
        resolved = sponsor_exists(sponsor["shortname"])
        assert ("url" in sponsor) == resolved, f"sponsor {sponsor} vs sponsors page"
        if resolved:
            assert sponsor["url"] == sponsor_link(sponsor["shortname"]), "sponsor url is the sponsor's own link, not the site stub page"

    people = [r for r in data["hosts"] + data["guests"] if "url" in r]
    for ref in people[:1]:
        assert api_request_context.get(urlparse(ref["url"]).path).status == 200, f"{ref['url']} does not resolve"


@mark.parametrize("show", SHOW_PARAMS)
def test_episodes_json_entries_link_to_episode_json(api_request_context: APIRequestContext, show: Show):
    """
    Every episodes.json entry carries a json_url; the newest and oldest resolve to that episode's JSON
    """
    entries = get_json(api_request_context, f"/show/{show.slug}/episodes.json")["episodes"]
    for entry in entries:
        expected = rf"{HOST}/show/{show.slug}/{re.escape(str(entry['slug']).lower())}\.json"
        assert re.fullmatch(expected, entry["json_url"]), f"{entry['slug']}: {entry.get('json_url')}"

    for entry in (entries[0], entries[-1]):
        episode = get_json(api_request_context, urlparse(entry["json_url"]).path)
        assert episode["type"] == "episode"
        assert episode["episode"] == entry["episode"]


def test_json_text_is_not_html_escaped(api_request_context: APIRequestContext):
    """
    '&', '<' and '>' appear as themselves in the raw text, not as \\u0026 and friends, so grep and agents can read it
    """
    ep = load_episode(CONTENT_SHOW / "linux-action-news" / "0129.md")
    assert any("&" in tag for tag in ep.data["tags"]), "fixture episode must have an '&' in a tag"
    text = api_request_context.get(episode_json_path(ep)).text()
    assert " & " in text
    assert "\\u0026" not in text
