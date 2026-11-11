import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Page, expect

from episode_data import CONTENT, CONTENT_SHOW, META_FILES, load_episode

GUEST_SAMPLE = 3


@dataclass(frozen=True)
class Person:
    username: str
    type: str
    title: str
    archived: bool


def _field(text: str, key: str) -> str | None:
    # flat YAML front matter; the test image has no YAML parser
    match = re.search(rf"^{key}: *[\"']?(.+?)[\"']?\s*$", text, re.M)
    return match.group(1) if match else None


def _load_person(path: Path) -> Person:
    text = path.read_text()
    return Person(
        username=_field(text, "username") or path.stem,
        type=_field(text, "type") or "",
        title=_field(text, "title") or "",
        archived=_field(text, "is_archived") == "true",
    )


PEOPLE: dict[str, Person] = {p.username: p for p in map(_load_person, sorted((CONTENT / "people").glob("*.md")))}
EPISODES = [load_episode(p) for p in sorted(CONTENT_SHOW.glob("*/*.md")) if p.name not in META_FILES]
HOSTED = Counter(h for e in EPISODES for h in set(e.data.get("hosts") or []))
GUESTED = Counter(g for e in EPISODES for g in set(e.data.get("guests") or []))
SHOW_HOSTS: dict[str, list[str]] = {
    d.name: json.loads(m.group(1)) if (m := re.search(r"^hosts\s*=\s*(\[.*\])", (d / "_index.md").read_text(), re.M)) else []
    for d in sorted(CONTENT_SHOW.iterdir())
    if (d / "_index.md").exists()
}


# people with no episodes (so no taxonomy page) re-added by the people scraper; their removal is tracked
#   on another branch. Named, not inferred, so any new episode-less person still fails.
NO_EPISODE_PEOPLE = {"jnsgruk", "joe", "joeres", "michaetunnell"}


def _link_param(person: Person):
    marks = []
    if person.username in NO_EPISODE_PEOPLE:
        marks = [mark.xfail(strict=True, reason="no episodes, so no taxonomy page (people scraper, fixed on another branch)")]
    return param(person, id=person.username, marks=marks)


# who /people/ links to (themes/jb/layouts/people/list.html)
LISTED_PEOPLE = [
    p for p in PEOPLE.values() if p.type == "guest" or (p.type == "host" and not p.archived)
]
HOST_TERMS = sorted(u for u, p in PEOPLE.items() if p.type == "host" and not p.archived and HOSTED[u])
SAMPLE_GUESTS = sorted(
    (u for u, p in PEOPLE.items() if p.type == "guest" and GUESTED[u]),
    key=lambda u: (-GUESTED[u], u),
)[:GUEST_SAMPLE]


@mark.parametrize("person", [_link_param(p) for p in LISTED_PEOPLE])
def test_people_list_link_target(api_request_context: APIRequestContext, person: Person):
    """
    Every host/guest card on /people/ links to a page that exists
    """
    path = f"/{person.type}s/{person.username}/"
    response = api_request_context.get(path)
    assert response.status == 200, f"{path} returned {response.status}"


def _expect_person_page(page: Page, person: Person, shows: set[str], episodes: int):
    expect(page.locator("h2.title").first).to_have_text(re.compile(rf"^\s*{person.type.title()} - {re.escape(person.title)}\s*$"))
    expect(page.locator("h2.title", has_text=f"Shows with {person.title}")).to_have_count(1)
    show_links = page.locator(".column.is-one-thirds .card a")
    hrefs = {re.sub(r"^https?://[^/]+", "", h) for h in (show_links.nth(i).get_attribute("href") for i in range(show_links.count()))}
    assert hrefs == {f"/show/{s}/" for s in shows}
    expect(page.locator("h2.title", has_text=f"Latest Episodes with {person.title}")).to_have_count(1)
    expect(page.locator(".section .card-episode")).to_have_count(episodes)


@mark.only_browser("chromium")
@mark.parametrize("username", HOST_TERMS)
def test_host_page(page: Page, username: str):
    """
    Host page shows the person's name, the shows they host, and a card per hosted episode
    """
    person = PEOPLE[username]
    # shows list the host in _index.md; a host only on episodes falls back to those episodes' shows
    shows = {s for s, hosts in SHOW_HOSTS.items() if username in hosts} or {
        e.show for e in EPISODES if username in (e.data.get("hosts") or [])
    }
    page.goto(f"/hosts/{username}/")
    _expect_person_page(page, person, shows, HOSTED[username])


@mark.only_browser("chromium")
@mark.parametrize("username", SAMPLE_GUESTS)
def test_guest_page(page: Page, username: str):
    """
    Guest page shows the person's name, the shows they've been on, and a card per episode
    """
    person = PEOPLE[username]
    shows = {e.show for e in EPISODES if username in (e.data.get("guests") or [])}
    page.goto(f"/guests/{username}/")
    _expect_person_page(page, person, shows, GUESTED[username])
