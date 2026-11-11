import re
from dataclasses import dataclass
from pathlib import Path

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Locator, Page, expect

from episode_data import CONTENT

REPO_ROOT = CONTENT.parent
CONFIG = (REPO_ROOT / "config.toml").read_text()
GITHUB_REPO = re.search(
    r'^github_repo\s*=\s*"(.*)"', (REPO_ROOT / "config/_default/params.toml").read_text(), re.M
).group(1)


@dataclass(frozen=True)
class CommunityPage:
    slug: str
    title: str
    link: str  # direct_link, or the page's own path
    draft: bool


def _toml_field(text: str, key: str) -> str | None:
    match = re.search(rf'^{key}\s*=\s*"?(.*?)"?\s*$', text, re.M)
    return match.group(1) if match else None


def _load_community(path: Path) -> CommunityPage:
    text = path.read_text()
    return CommunityPage(
        slug=path.stem,
        title=_toml_field(text, "title"),
        link=_toml_field(text, "direct_link") or f"/community/{path.stem}/",
        draft=_toml_field(text, "draft") == "true",
    )


COMMUNITY = [_load_community(p) for p in sorted((CONTENT / "community").glob("*.md")) if p.name != "_index.md"]
# the dev server renders drafts (-D) but production doesn't, so drafts may or may not be listed
REQUIRED_LINKS = {c.link for c in COMMUNITY if not c.draft}
ALLOWED_LINKS = {c.link for c in COMMUNITY}


def _hrefs(links: Locator) -> set[str]:
    return {re.sub(r"^https?://(localhost|127\.0\.0\.1|jb-com)(:\d+)?", "", links.nth(i).get_attribute("href")) for i in range(links.count())}


def _menu(name: str) -> list[tuple[str, str]]:
    blocks = re.findall(rf"^\[\[Menu\.{name}\]\]\n((?:[ \t]+.*\n)+)", CONFIG, re.M)
    return [(_toml_field(b.replace("    ", ""), "name"), _toml_field(b.replace("    ", ""), "url")) for b in blocks]


@mark.only_browser("chromium")
def test_community_index(page: Page):
    """
    /community/ has one card per community page, linking to its direct_link or its own page
    """
    page.goto("/community/")
    rendered = _hrefs(page.locator(".section .columns a"))
    assert REQUIRED_LINKS <= rendered <= ALLOWED_LINKS, f"unexpected cards: {rendered - ALLOWED_LINKS}, missing: {REQUIRED_LINKS - rendered}"
    for community in COMMUNITY:
        if community.link in rendered:
            expect(page.locator(".card-header-title", has_text=re.compile(rf"^\s*{re.escape(community.title)}\s*$"))).to_have_count(1)


@mark.parametrize(
    "community",
    [param(c, id=c.slug) for c in COMMUNITY if c.link.startswith("/") and not c.draft],
)
def test_community_subpage(api_request_context: APIRequestContext, community: CommunityPage):
    """
    Community pages without a direct_link have their own page
    """
    response = api_request_context.get(community.link)
    assert response.status == 200, f"{community.link} returned {response.status}"
    title = re.search(r"<title[^>]*>(.*?)</title>", response.text())
    assert title and title.group(1).startswith(f"{community.title} | "), f"<title> is {title and title.group(1)!r}"


@mark.only_browser("chromium")
def test_footer_community_links(page: Page):
    """
    The footer's first link column lists the same community links as /community/
    """
    page.goto("/")
    column = page.locator("footer .columns").first.locator(".column").nth(1)
    rendered = _hrefs(column.locator("a"))
    assert REQUIRED_LINKS <= rendered <= ALLOWED_LINKS, f"unexpected: {rendered - ALLOWED_LINKS}, missing: {REQUIRED_LINKS - rendered}"


@mark.only_browser("chromium")
@mark.parametrize(
    "path, edit_url",
    [
        param("/", f"{GITHUB_REPO}/blob/main/themes/jb/layouts/index.html", id="home"),
        param("/membership/", f"{GITHUB_REPO}/tree/main/content/membership/index.md", id="membership"),
        param("/community/irc/", f"{GITHUB_REPO}/tree/main/content/community/irc.md", id="community-irc"),
    ],
)
def test_footer_involved_links(page: Page, path: str, edit_url: str):
    """
    The footer's last column has the FooterRight menu from config.toml and an edit link to the page's source
    """
    page.goto(path)
    column = page.locator("footer .columns").first.locator(".column").last
    for name, url in _menu("FooterRight"):
        expect(column.get_by_role("link", name=name, exact=True)).to_have_attribute("href", url)
    expect(column.get_by_role("link", name="Edit this page on GitHub")).to_have_attribute("href", edit_url)


@dataclass(frozen=True)
class Pick:
    title: str
    url: str
    episodes: tuple[str, ...]  # /show/<slug>/<episode>


def _load_pick(path: Path) -> Pick:
    # flat YAML apart from the shows list; the test image has no YAML parser
    text = path.read_text()
    shows = re.split(r"^- ", text.split("\nshows:\n", 1)[1], flags=re.M)[1:] if "\nshows:\n" in text else []
    episodes = []
    for entry in shows:
        fields = dict(re.findall(r"^\s*(episode|slug):\s*['\"]?([^'\"\n]+)", entry, re.M))
        if fields.keys() >= {"episode", "slug"}:
            episodes.append(f"/show/{fields['slug']}/{fields['episode']}")
    return Pick(
        title=re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", text, re.M).group(1),
        url=re.search(r"^url:\s*(\S+)", text, re.M).group(1),
        episodes=tuple(episodes),
    )


PICKS = [_load_pick(p) for p in sorted((REPO_ROOT / "data/picks").glob("*.yaml"))]


@mark.only_browser("chromium")
def test_picks_page(page: Page):
    """
    /community/picks/ has one card per data/picks file, with its link and one badge per episode it was picked on
    """
    page.goto("/community/picks/")
    cards = page.locator(".pick.card")
    expect(cards).to_have_count(len(PICKS))
    rendered = {
        (card["url"], tuple(card["episodes"]))
        for card in cards.evaluate_all(
            "cards => cards.map(c => ({url: c.querySelector('h4 a').getAttribute('href'),"
            " episodes: [...c.querySelectorAll('a.control')].map(a => a.getAttribute('href'))}))"
        )
    }
    assert rendered == {(p.url, p.episodes) for p in PICKS}


def test_picks_episode_links(api_request_context: APIRequestContext):
    """
    Every episode a pick links to exists
    """
    links = sorted({e for p in PICKS for e in p.episodes})
    broken = [link for link in links if api_request_context.get(f"{link}/").status != 200]
    assert not broken, f"pick episode links that 404: {broken}"
