"""
JSON twins of shows and episodes: /show/<slug>/show.json and /show/<slug>/<NNNN>.json (schema in docs/json-schema.md).

Expected values come from content/ so the tests hold for any content snapshot.
Links may be absolute (production) or site-relative (CI builds with baseURL "/").
"""
import json
import re
import tomllib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Page, expect

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
    sponsor_link,
    sponsor_path,
    yaml_title,
)

HOST = r"(?:https?://[^/)\s]+)?"


@dataclass(frozen=True)
class Show:
    slug: str
    params: dict = field(compare=False, hash=False, repr=False)
    episodes: tuple[Episode, ...] = field(compare=False, hash=False, repr=False)  # oldest first

    @property
    def title(self) -> str:
        return self.params["title"]


def _toml_front_matter(path: Path) -> dict:
    return tomllib.loads(path.read_text().split("+++")[1])


SHOWS: list[Show] = [
    Show(
        slug=d.name,
        params=_toml_front_matter(d / "_index.md"),
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


def site_url(path: str) -> str:
    """
    Pattern for a site path rendered through absURL/Permalink
    """
    return rf"{HOST}{re.escape(path)}"


def assert_person_ref(ref: dict, where: str):
    if person_type(ref["slug"]) is None:
        assert set(ref) == {"slug"}, f"{where} {ref}: no people page, so only the slug"
    else:
        assert ref["name"] == yaml_title(CONTENT / "people" / f"{ref['slug']}.md"), f"{where} {ref}: name"
        assert re.fullmatch(site_url(f"/people/{ref['slug']}/"), ref["url"]), f"{where} {ref}: url"


@mark.parametrize("show", SHOW_PARAMS)
def test_show_json(api_request_context: APIRequestContext, show: Show):
    """
    show.json carries the show facts from _index.md, counts match content, and links to the other twins
    """
    base = f"/show/{show.slug}"
    data = get_json(api_request_context, f"{base}/show.json")
    p = show.params
    newest = show.episodes[-1]

    assert find_nulls(data) == [], "null fields must be omitted at every depth"
    assert data["schema_version"] == 1
    assert data["type"] == "show"
    assert data["slug"] == show.slug
    assert data["name"] == show.title
    assert re.fullmatch(site_url(f"{base}/"), data["url"])
    assert data["active"] == p.get("active", False)
    assert data.get("description") == (p.get("description") or None)
    if p.get("header_image"):
        assert re.fullmatch(site_url(p["header_image"]), data["header_image"])
    else:
        assert "header_image" not in data
    assert data["episode_count"] == len(show.episodes)
    assert data["latest_episode"]["episode"] == newest.data["episode"]
    assert re.fullmatch(site_url(newest.url), data["latest_episode"]["url"])
    assert re.fullmatch(site_url(f"{newest.url.rstrip('/')}.md"), data["latest_episode"]["markdown_url"])
    assert "json_url" not in data, "a show's own JSON URL is the URL it was fetched from"
    assert re.fullmatch(site_url(f"{base}/show.md"), data["markdown_url"])
    assert re.fullmatch(site_url(f"{base}/episodes.json"), data["episodes_url"])
    assert re.fullmatch(site_url(f"{base}/llms.txt"), data["llms_url"])

    assert [h["slug"] for h in data["hosts"]] == p["hosts"], "hosts keep front matter order"
    for host in data["hosts"]:
        assert_person_ref(host, "host")

    assert "numbered_episodes" not in data and "special_episodes" not in data, "episodes.json lists every episode"
    assert "podverse_podcast_id" not in data
    podverse = p.get("podverse_podcast_id")
    assert data.get("podverse_url") == (f"https://podverse.fm/podcast/{podverse}" if podverse else None)

    links = {name: link["url"] for name, link in (p.get("links") or {}).items() if link.get("url")}
    assert data["links"].keys() == links.keys()
    for name, url in links.items():
        expected = site_url(url) if url.startswith("/") else re.escape(url)
        assert re.fullmatch(expected, data["links"][name]), f"link {name}: {data['links'][name]}"


# the-launch T-0: uppercase slug, non-numeric episode number; coder-radio 3: video, alt and ogg audio
CORE_EPISODES: list[Episode] = list(
    {
        e.url: e
        for e in [
            *sample_episodes(),
            load_episode(CONTENT_SHOW / "the-launch" / "T-0.md"),
            load_episode(CONTENT_SHOW / "coder-radio" / "0003.md"),
        ]
    }.values()
)
EPISODE_PARAMS = [param(e, id=e.url, marks=mark.episodes) for e in CORE_EPISODES]


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
        assert data["audio"].get("bytes") == (d.get("podcast_bytes") or None)
        assert data["audio"].get("duration") == (d.get("podcast_duration") or None)
    else:
        assert "audio" not in data
    assert data.get("audio_alt_url") == (d.get("podcast_alt_file") or None)
    assert data.get("audio_ogg_url") == (d.get("podcast_ogg_file") or None)
    video = {
        out: d[key]
        for out, key in (("url", "video_file"), ("hd_url", "video_hd_file"), ("mobile_url", "video_mobile_file"))
        if d.get(key)
    }
    assert data.get("video") == (video or None)
    if d.get("header_image"):
        assert re.fullmatch(site_url(d["header_image"]), data["header_image"])
    else:
        assert "header_image" not in data

    assert re.fullmatch(site_url(ep.url), data["url"])
    assert "json_url" not in data, "an episode's own JSON URL is the URL it was fetched from"
    assert re.fullmatch(site_url(f"{ep.url.rstrip('/')}.md"), data["markdown_url"])
    show = f"/show/{ep.show}"
    assert data["show"]["slug"] == ep.show
    assert data["show"]["name"] == _toml_front_matter(CONTENT_SHOW / ep.show / "_index.md")["title"]
    assert re.fullmatch(site_url(f"{show}/"), data["show"]["url"])
    assert re.fullmatch(site_url(f"{show}/show.json"), data["show"]["json_url"])
    assert re.fullmatch(site_url(f"{show}/show.md"), data["show"]["markdown_url"])
    assert re.fullmatch(site_url(f"{show}/llms.txt"), data["show"]["llms_url"])
    assert find_nulls(data) == [], "null fields must be omitted at every depth"

    assert "podverse_url" not in data, "podverse.fm episode pages use Podverse's own id, which the guid cannot give us"


def test_core_episodes_cover_every_optional_field():
    """
    Guard: the core sample must exercise each optional episode field, or test_episode_json_core checks it only as absent
    """
    keys = ("podcast_alt_file", "podcast_ogg_file", "video_file", "header_image", "podcast_chapters", "transcripts", "youtube_link")
    missing = [k for k in keys if not any(e.data.get(k) for e in CORE_EPISODES)]
    assert not missing, f"no core episode has {missing}"


@mark.parametrize("show", SHOW_PARAMS)
def test_show_json_links_resolve(api_request_context: APIRequestContext, show: Show):
    """
    show.json latest_episode.json_url and the oldest episodes.json entry's json_url lead to that episode's JSON
    """
    latest = get_json(api_request_context, f"/show/{show.slug}/show.json")["latest_episode"]
    oldest = get_json(api_request_context, f"/show/{show.slug}/episodes.json")["episodes"][-1]
    for ref in (latest, oldest):
        episode = get_json(api_request_context, urlparse(ref["json_url"]).path)
        assert episode["type"] == "episode"
        assert episode["episode"] == ref["episode"]


@mark.episodes
@mark.parametrize("show", SHOW_PARAMS)
def test_every_episode_json_is_valid(api_request_context: APIRequestContext, show: Show):
    """
    Every episode listed in episodes.json serves parseable JSON with schema_version 1 and type "episode"
    """
    entries = get_json(api_request_context, f"/show/{show.slug}/episodes.json")["episodes"]
    problems = []
    for entry in entries:
        path = urlparse(entry["json_url"]).path
        response = api_request_context.get(path)
        content_type = response.headers.get("content-type", "")
        if response.status != 200 or not content_type.startswith("application/json"):
            problems.append(f"{path}: {response.status} {content_type}")
            continue
        try:
            data = json.loads(response.text())
        except ValueError as e:
            problems.append(f"{path}: unparseable: {e}")
            continue
        if not isinstance(data, dict):
            problems.append(f"{path}: top level is {type(data).__name__}, not an object")
        elif (data.get("schema_version"), data.get("type"), data.get("episode")) != (1, "episode", entry["episode"]):
            problems.append(f"{path}: schema_version={data.get('schema_version')!r} type={data.get('type')!r} episode={data.get('episode')!r}")
    assert len(entries) == len(show.episodes)
    assert not problems, f"{len(problems)} bad file(s):\n" + "\n".join(problems[:20])


@mark.parametrize("ep", EPISODE_PARAMS)
def test_episode_json_refs(api_request_context: APIRequestContext, ep: Episode):
    """
    Hosts, guests and sponsors keep front matter order and resolve to names and URLs; refs without a page keep only the id
    """
    data = get_json(api_request_context, episode_json_path(ep))

    for key in ("hosts", "guests"):
        assert [r["slug"] for r in data[key]] == (ep.data.get(key) or [])
        for ref in data[key]:
            assert_person_ref(ref, key)

    assert [s["shortname"] for s in data["sponsors"]] == (ep.data.get("sponsors") or [])
    for sponsor in data["sponsors"]:
        if sponsor_exists(sponsor["shortname"]):
            assert sponsor["name"] == yaml_title(sponsor_path(sponsor["shortname"])), f"sponsor {sponsor}: name"
            assert sponsor["url"] == sponsor_link(sponsor["shortname"]), "sponsor url is the sponsor's own link, not the site stub page"
        else:
            assert set(sponsor) == {"shortname"}, f"sponsor {sponsor}: no sponsors page, so only the shortname"

    people = [r for r in data["hosts"] + data["guests"] if "url" in r]
    for ref in people[:1]:
        assert api_request_context.get(urlparse(ref["url"]).path).status == 200, f"{ref['url']} does not resolve"


@mark.parametrize(
    "path, raw, escaped",
    [
        param(CONTENT_SHOW / "linux-action-news" / "0129.md", " & ", "\\u0026", id="ampersand"),
        param(CONTENT_SHOW / "jupiter-extras" / "0028.md", "<3", "\\u003c", id="less-than"),
        param(CONTENT_SHOW / "office-hours" / "0011.md", " > ", "\\u003e", id="greater-than"),
    ],
)
def test_json_text_is_not_html_escaped(api_request_context: APIRequestContext, path: Path, raw: str, escaped: str):
    """
    '&', '<' and '>' appear as themselves in the raw text, not as \\u0026 and friends, so grep and agents can read it
    """
    ep = load_episode(path)
    assert raw in json.dumps(ep.data, ensure_ascii=False), f"fixture episode must contain {raw!r}"
    response = api_request_context.get(episode_json_path(ep))
    assert response.status == 200
    text = response.text()
    assert raw in text
    assert escaped not in text


@mark.only_browser("chromium")
@mark.parametrize("ep", EPISODE_PARAMS)
def test_episode_page_links_to_its_json(page: Page, ep: Episode):
    """
    The episode HTML head advertises its JSON twin, so a crawler or agent can find it from the page
    """
    page.goto(ep.url)
    links = page.locator('link[rel="alternate"][type="application/json"]')
    expect(links).to_have_count(1)
    expect(links).to_have_attribute("href", re.compile(rf"^{site_url(episode_json_path(ep))}$"))


@mark.only_browser("chromium")
@mark.parametrize("show", SHOW_PARAMS)
def test_show_page_links_to_show_and_episode_list_json(page: Page, show: Show):
    """
    The show HTML head advertises show.json and the full episodes.json
    """
    page.goto(f"/show/{show.slug}/")
    hrefs = page.locator('link[rel="alternate"][type="application/json"]').evaluate_all("els => els.map(e => e.href)")
    assert sorted(urlparse(h).path for h in hrefs) == [f"/show/{show.slug}/episodes.json", f"/show/{show.slug}/show.json"]


@mark.only_browser("chromium")
@mark.parametrize("path", ["/", "/community/", "/show/", "/people/chris/"])
def test_pages_without_json_advertise_none(page: Page, path: str):
    """
    Only shows and episodes have JSON twins; other pages must not advertise one
    """
    page.goto(path)
    expect(page.locator('link[rel="alternate"][type="application/json"]')).to_have_count(0)
