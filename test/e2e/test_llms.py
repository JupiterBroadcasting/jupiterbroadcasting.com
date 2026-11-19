"""
llms.txt machinery (llmstxt.org v2): /llms.txt, /llms-full.txt, per-show llms.txt + episodes.json,
markdown twins at <url>index.md, and discovery links in HTML heads.

Expected values come from content/ so the tests hold for any content snapshot.
Links may be absolute (production) or site-relative (CI builds with baseURL "/").
"""
import re
from dataclasses import dataclass
from pathlib import Path

from pytest import mark, param
from playwright.sync_api import APIRequestContext, APIResponse, Page, expect

from episode_data import CONTENT, CONTENT_SHOW, Episode, episodes_by_date, is_active, sample_episodes, sponsor_exists

HOST = r"(?:https?://[^/)\s]+)?"
LLMS_SECTIONS = ["/show/", "/hosts/", "/guests/"]
SITE_PAGES = ["/membership/", "/live/", "/community/", "/hosts/", "/sponsors/", "/contact/"]


def _yaml_field(path: Path, key: str) -> str | None:
    # flat YAML front matter; the test image has no YAML parser
    match = re.search(rf"^{key}: *[\"']?(.+?)[\"']?\s*$", path.read_text(), re.M)
    return match.group(1) if match else None


def _toml_field(path: Path, key: str) -> str:
    return re.search(rf'^{key}\s*=\s*"(.*)"\s*$', path.read_text(), re.M).group(1)


@dataclass(frozen=True)
class Show:
    slug: str
    title: str
    active: bool
    rss: str | None
    episodes: tuple[Episode, ...]  # oldest first

    @property
    def newest_first(self) -> list[Episode]:
        return list(reversed(self.episodes))


def _load_show(show_dir: Path) -> Show:
    episodes = [e for e in episodes_by_date(show_dir) if e.data.get("type") == "episode"]
    return Show(
        slug=show_dir.name,
        title=_toml_field(show_dir / "_index.md", "title"),
        active=is_active(show_dir),
        rss=_yaml_field(show_dir / "subscribe.md", "rss") if (show_dir / "subscribe.md").exists() else None,
        episodes=tuple(episodes),
    )


SHOWS: list[Show] = [_load_show(d) for d in sorted(CONTENT_SHOW.iterdir()) if (d / "_index.md").exists()]
SHOW_PARAMS = [param(s, id=s.slug) for s in SHOWS]

ACTIVE_HOSTS: list[str] = sorted(
    p.stem
    for p in (CONTENT / "people").glob("*.md")
    if _yaml_field(p, "type") == "host" and _yaml_field(p, "is_archived") != "true"
)

# a hosts term only exists once the person hosts an episode
HOST_TERMS: list[str] = sorted(
    {h for show in SHOWS for e in show.episodes for h in e.data.get("hosts") or []} & set(ACTIVE_HOSTS)
)

SAMPLE_EPISODES: list[Episode] = sample_episodes()


def _get(api: APIRequestContext, path: str, content_type: str) -> APIResponse:
    response = api.get(path)
    assert response.status == 200, f"{path}: expected 200, got {response.status}"
    assert response.headers["content-type"].startswith(content_type), (
        f"{path}: expected {content_type}, got {response.headers['content-type']}"
    )
    return response


def _section(text: str, heading: str, until: str | None = None) -> str:
    assert heading in text, f"missing heading {heading!r}"
    body = text.split(heading, 1)[1]
    if until:
        assert until in body, f"missing heading {until!r} after {heading!r}"
        body = body.split(until, 1)[0]
    return body


def _episode_date(ep: Episode) -> str:
    # Hugo formats .Date in the front matter's own offset, so the date part is the local date
    return str(ep.data["date"])[:10]


def _slug(ep: Episode) -> str:
    return str(ep.data.get("slug") or ep.number)


def test_root_llms_txt(api_request_context: APIRequestContext):
    """
    /llms.txt follows the spec layout: H1, summary blockquote, then Shows / Site / Optional sections in order
    """
    text = _get(api_request_context, "/llms.txt", "text/plain").text()
    assert text.startswith("# Jupiter Broadcasting\n"), "H1 must be the first line"
    assert "\n> " in text, "missing summary blockquote"
    positions = [text.find(h) for h in ("## Shows", "## Site", "## Optional")]
    assert -1 not in positions and positions == sorted(positions), "sections missing or out of order"
    assert re.search(rf"\]\({HOST}/llms-full\.txt\)", text), "Optional must link llms-full.txt"


def test_root_shows_match_navigation(
    api_request_context: APIRequestContext, expected_dropdown_items: dict[str, list[dict[str, str]]]
):
    """
    ## Shows lists exactly the shows in the navbar Shows dropdown
    """
    shows = _section(_get(api_request_context, "/llms.txt", "text/plain").text(), "## Shows", "## Site")
    listed = set(re.findall(rf"\]\({HOST}(/show/[^/]+/)llms\.txt\)", shows))
    assert listed == {item["href"] for item in expected_dropdown_items["Shows"]}


@mark.parametrize("show", SHOW_PARAMS)
def test_root_show_entry(api_request_context: APIRequestContext, show: Show):
    """
    Active shows are under ## Shows linking their llms.txt, archived ones under ## Optional linking their
    markdown twin; both carry the content episode count and the subscribe page RSS feed
    """
    text = _get(api_request_context, "/llms.txt", "text/plain").text()
    if show.active:
        section, target = _section(text, "## Shows", "## Site"), "llms.txt"
    else:
        section, target = _section(text, "## Optional"), "index.md"

    entry = re.search(
        rf"^- \[{re.escape(show.title.strip())}\]\({HOST}/show/{show.slug}/{re.escape(target)}\): "
        rf"(\d+) episodes\.(.*)$",
        section,
        re.M,
    )
    assert entry, f"{show.slug} not listed under the expected section"
    assert int(entry.group(1)) == len(show.episodes), "episode count differs from content"
    if show.rss:
        assert f"[RSS]({show.rss})" in entry.group(2), "missing RSS link"


def test_root_site_links(api_request_context: APIRequestContext):
    """
    ## Site links each core page's markdown twin, and the twin resolves
    """
    site = _section(_get(api_request_context, "/llms.txt", "text/plain").text(), "## Site", "## Optional")
    for path in SITE_PAGES:
        assert re.search(rf"\]\({HOST}{re.escape(path)}index\.md\)", site), f"{path} not linked"
        _get(api_request_context, f"{path}index.md", "text/markdown")


def test_llms_full_txt(api_request_context: APIRequestContext):
    """
    /llms-full.txt concatenates core pages as plain markdown: no front matter, no HTML escaping
    """
    text = _get(api_request_context, "/llms-full.txt", "text/plain").text()
    assert "Membership" in text
    assert "Brent Gervais" in text
    assert "+++" not in text, "TOML front matter leaked"
    assert "avatar_small" not in text, "YAML front matter leaked"
    assert "&#43;" not in text and "&amp;" not in text, "HTML escaping in plain text output"


@mark.parametrize("path", LLMS_SECTIONS)
def test_llms_only_on_show_sections(api_request_context: APIRequestContext, path: str):
    """
    llms output is enabled per show in front matter, not for every section
    """
    response = api_request_context.get(f"{path}llms.txt")
    assert response.status == 404, f"{path}llms.txt should not exist, got {response.status}"


@mark.parametrize("show", SHOW_PARAMS)
def test_show_llms_txt(api_request_context: APIRequestContext, show: Show):
    """
    Per-show llms.txt is curated: the 10 newest episodes plus an archive summary pointing at episodes.json
    """
    text = _get(api_request_context, f"/show/{show.slug}/llms.txt", "text/plain").text()
    assert text.startswith(f"# {show.title}\n"), "H1 must be the show title"
    assert len(text) < 20_000, "per-show llms.txt should be curated, not a full index"
    assert re.search(rf"\]\({HOST}/show/{show.slug}/episodes\.json\)", text), "missing episodes.json link"
    assert re.search(rf"\]\({HOST}/show/{show.slug}/index\.md\)", text), "missing show twin link"

    recent = _section(text, f"## Most recent episodes (of {len(show.episodes)})", "## Episode archive")
    entries = re.findall(rf"^- \[(\d{{4}}-\d{{2}}-\d{{2}}) · .*\]\({HOST}(/show/{show.slug}/[^/]+/)index\.md\)", recent, re.M)
    assert [d for d, _ in entries] == [_episode_date(e) for e in show.newest_first[:10]], (
        "recent episodes must be the 10 newest, newest first"
    )

    numbered = [int(e.number) for e in show.episodes if e.number.isdigit()]
    archive = _section(text, "## Episode archive")
    assert f"{len(numbered)} numbered episodes, {min(numbered)}-{max(numbered)}." in archive
    specials = len(show.episodes) - len(numbered)
    if specials:
        assert f"Plus {specials} special episodes" in archive


@mark.parametrize("show", SHOW_PARAMS)
def test_show_episodes_json(api_request_context: APIRequestContext, show: Show):
    """
    episodes.json enumerates every episode in content (incl. prefixed specials like the-launch T-0), newest first
    """
    data = _get(api_request_context, f"/show/{show.slug}/episodes.json", "application/json").json()
    assert data["show"] == show.slug
    assert data["title"] == show.title
    assert data["count"] == len(show.episodes), "count differs from content"
    assert len(data["episodes"]) == data["count"]
    assert {e["slug"] for e in data["episodes"]} == {_slug(e) for e in show.episodes}

    dates = [e["date"] for e in data["episodes"]]
    assert dates == sorted(dates, reverse=True), "episodes must be newest first"

    for ep in data["episodes"]:
        assert ep["title"], f"{ep['slug']}: empty title"
        assert re.fullmatch(rf"{HOST}/show/{show.slug}/{re.escape(ep['slug'].lower())}/", ep["url"]), ep["url"]
        assert isinstance(ep["hosts"], (list, type(None))), f"{ep['slug']}: hosts"
        assert isinstance(ep["guests"], (list, type(None))), f"{ep['slug']}: guests"
        assert all(t["url"] for t in ep["transcripts"] or []), f"{ep['slug']}: transcript without url"


@mark.parametrize("show", SHOW_PARAMS)
def test_show_llms_newest_oldest_match_json(api_request_context: APIRequestContext, show: Show):
    """
    The Newest/Oldest twin links in llms.txt agree with the episodes.json ordering
    """
    text = _get(api_request_context, f"/show/{show.slug}/llms.txt", "text/plain").text()
    episodes = _get(api_request_context, f"/show/{show.slug}/episodes.json", "application/json").json()["episodes"]
    for label, ep in (("Newest", episodes[0]), ("Oldest", episodes[-1])):
        assert re.search(rf"{label}: `{HOST}/show/{show.slug}/{re.escape(ep['slug'].lower())}/index\.md`", text), label


@mark.parametrize("show", SHOW_PARAMS)
def test_show_markdown_twin(api_request_context: APIRequestContext, show: Show):
    """
    Show twin has the title, its URL, links to the show llms.txt and the RSS feed
    """
    text = _get(api_request_context, f"/show/{show.slug}/index.md", "text/markdown").text()
    assert text.startswith(f"# {show.title}\n"), "H1 must be the show title"
    assert re.search(rf"^URL: {HOST}/show/{show.slug}/$", text, re.M), "missing URL line"
    assert re.search(rf"\[llms\.txt\]\({HOST}/show/{show.slug}/llms\.txt\)", text), "missing llms.txt link"
    if show.rss:
        assert f"RSS feed: [{show.rss}]({show.rss})" in text
    assert "{{" not in text and "+++" not in text, "template or front matter leaked"


@mark.parametrize("ep", [param(e, id=e.url, marks=mark.episodes) for e in SAMPLE_EPISODES])
def test_episode_markdown_twin(api_request_context: APIRequestContext, ep: Episode):
    """
    Episode twin resolves at the lowercase permalink and carries the front matter facts
    """
    text = _get(api_request_context, f"{ep.url}index.md", "text/markdown").text()
    assert text.splitlines()[0].strip() == f"# {ep.data['title']}".strip(), "H1 must be the episode title"
    assert re.search(rf"^URL: {HOST}{re.escape(ep.url)}$", text, re.M), "missing URL line"
    assert f"- Episode: {ep.number}\n" in text
    assert f"- Date: {_episode_date(ep)}\n" in text
    if ep.data.get("hosts"):
        assert f"- Hosts: {', '.join(ep.data['hosts'])}\n" in text
    if ep.data.get("guests"):
        assert f"- Guests: {', '.join(ep.data['guests'])}\n" in text
    for transcript in ep.data.get("transcripts") or []:
        assert f"]({transcript['url']})" in text, f"missing transcript {transcript['url']}"
    sponsors = [s for s in ep.data.get("sponsors") or [] if sponsor_exists(s)]
    if sponsors:
        assert "\nSponsors:\n" in text
        assert len(re.findall(rf"^- \[.+\]\({HOST}/sponsors/[^)]+index\.md\)", text, re.M)) == len(sponsors)
    assert "{{" not in text and "+++" not in text, "template or front matter leaked"


def test_hosts_twin_lists_active_hosts(api_request_context: APIRequestContext):
    text = _get(api_request_context, "/hosts/index.md", "text/markdown").text()
    missing = [h for h in HOST_TERMS if not re.search(rf"\]\({HOST}/hosts/{h}/index\.md\)", text)]
    assert not missing, f"active hosts missing from /hosts/index.md: {missing}"


@mark.parametrize("username", HOST_TERMS)
def test_host_term_twin(api_request_context: APIRequestContext, username: str):
    """
    Host term twin shows the person's real name and people-page details, then their episodes
    """
    person = CONTENT / "people" / f"{username}.md"
    text = _get(api_request_context, f"/hosts/{username}/index.md", "text/markdown").text()
    assert text.startswith(f"# {_yaml_field(person, 'title')}\n"), "H1 must be the real name, not the slug"
    assert f"Username: {username}\n" in text
    homepage = _yaml_field(person, "homepage")
    if homepage and homepage != "null":
        assert f"Homepage: {homepage}" in text
    assert re.search(rf"\]\({HOST}/show/[^)]+/index\.md\)", text), "term twin must list episodes"


@mark.parametrize("username", ACTIVE_HOSTS)
def test_people_twin(api_request_context: APIRequestContext, username: str):
    person = CONTENT / "people" / f"{username}.md"
    text = _get(api_request_context, f"/people/{username}/index.md", "text/markdown").text()
    assert text.startswith(f"# {_yaml_field(person, 'title')}\n")
    assert f"Username: {username}\n" in text
    assert re.search(rf"\]\({HOST}/hosts/{username}/index\.md\)", text), "missing link to hosts term twin"


def test_guests_twin(api_request_context: APIRequestContext):
    text = _get(api_request_context, "/guests/index.md", "text/markdown").text()
    assert re.search(rf"\]\({HOST}/guests/[^/]+/index\.md\)", text), "guests twin lists no guests"
    assert "{{" not in text, "template error"


@mark.only_browser("chromium")
def test_home_discovery_link(page: Page):
    """
    Home points at /llms.txt; it has no markdown twin (home outputs are html, rss, llms, llmsfull)
    """
    page.goto("/")
    expect(page.locator('link[rel="describedby"]')).to_have_attribute("href", re.compile(rf"^{HOST}/llms\.txt$"))
    expect(page.locator('link[rel="alternate"][type="text/markdown"]')).to_have_count(0)


@mark.only_browser("chromium")
@mark.parametrize(
    "path, llms",
    [param("/community/", "/llms.txt", id="community")]
    + [param(f"/show/{s.slug}/", f"/show/{s.slug}/llms.txt", id=s.slug) for s in SHOWS]
    + [param(SAMPLE_EPISODES[0].url, f"/show/{SAMPLE_EPISODES[0].show}/llms.txt", id="episode")],
)
def test_discovery_links(page: Page, path: str, llms: str):
    """
    Every page points at its nearest llms.txt (describedby) and its markdown twin (alternate)
    """
    page.goto(path)
    expect(page.locator('link[rel="describedby"]')).to_have_attribute("href", re.compile(rf"^{HOST}{re.escape(llms)}$"))
    expect(page.locator('link[rel="alternate"][type="text/markdown"]')).to_have_attribute(
        "href", re.compile(rf"^{HOST}{re.escape(path)}index\.md$")
    )
