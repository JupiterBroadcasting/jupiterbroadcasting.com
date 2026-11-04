import json
import math
import re
from pathlib import Path

from pytest import fixture, mark, param
from playwright.sync_api import Page, expect

REPO_ROOT = Path(__file__).parents[2]
SHOW_DIR = REPO_ROOT / "content/show"
PEOPLE_DIR = REPO_ROOT / "content/people"


try:
    from tomllib import loads as toml_loads
except ImportError:
    # The jb_tests image runs Python 3.10 with no TOML library; the show front
    # matter only uses tables and JSON-compatible scalars/arrays.
    def toml_loads(text: str) -> dict:
        root: dict = {}
        table = root
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("["):
                table = root
                for part in line.strip("[]").split("."):
                    table = table.setdefault(part, {})
                continue
            key, _, value = line.partition("=")
            table[key.strip()] = json.loads(value.strip())
        return root


PAGINATE = int(
    re.search(r"^paginate\s*=\s*(\d+)", (REPO_ROOT / "config.toml").read_text(), re.M).group(1)
)


def _front_matter(path: Path) -> dict:
    match = re.match(r"\+\+\+\n(.*?)\n\+\+\+", path.read_text(), re.DOTALL)
    return toml_loads(match.group(1))


SHOWS = {
    show_dir.name: _front_matter(show_dir / "_index.md")
    for show_dir in sorted(SHOW_DIR.iterdir())
    if (show_dir / "_index.md").exists()
}
SHOWS_WITH_HOSTS = [slug for slug, fm in SHOWS.items() if "hosts" in fm]
HOST_PARAMS = [
    param(
        slug,
        id=slug,
        marks=mark.xfail(
            reason="content/people/michael.md has type: guest, so the Coder Radio host "
            "list links him to /guests/michael/ instead of /hosts/michael/"
        ),
    )
    if slug == "coder-radio"
    else param(slug, id=slug)
    for slug in SHOWS_WITH_HOSTS
]


def _episode_count(slug: str) -> int:
    return sum(
        '"type": "episode"' in f.read_text() for f in (SHOW_DIR / slug).glob("*.md")
    )


@fixture
def show(page: Page, request) -> dict:
    """
    Navigate to the parametrized show page and return its front matter
    """
    slug = request.param
    page.goto(f"/show/{slug}/")
    return SHOWS[slug]


@mark.only_browser("chromium")
@mark.parametrize("show", HOST_PARAMS, indirect=True)
def test_show_hosts(page: Page, show: dict):
    """
    Ensure every host in the show's front matter has a people page and is
    rendered in the host list
    """
    missing = [h for h in show["hosts"] if not (PEOPLE_DIR / f"{h}.md").exists()]
    assert not missing, f"hosts without content/people/<username>.md: {missing}"

    links = page.locator('.host-list a[href^="/hosts/"]')
    hrefs = {links.nth(i).get_attribute("href") for i in range(links.count())}
    assert hrefs == {f"/hosts/{h}/" for h in show["hosts"]}


@mark.only_browser("chromium")
@mark.parametrize("show", SHOWS_WITH_HOSTS, ids=SHOWS_WITH_HOSTS, indirect=True)
def test_show_link_icons(page: Page, show: dict):
    """
    Ensure the subscribe icon and one icon per front matter link are rendered
    """
    level = page.locator(".level")
    expect(level.locator('a.link[title="subscribe"]')).to_have_count(1)
    for key, value in show.get("links", {}).items():
        link = level.locator(f'a.link[title="{key}"]')
        expect(link).to_have_count(1)
        expect(link).to_have_attribute("href", value["url"])
    expect(level.locator("a.link")).to_have_count(1 + len(show.get("links", {})))


PAGINATED_SHOWS = [slug for slug in SHOWS if _episode_count(slug) > PAGINATE]


@mark.only_browser("chromium")
@mark.parametrize("show", PAGINATED_SHOWS, ids=PAGINATED_SHOWS, indirect=True)
def test_show_pagination(page: Page, show: dict, request):
    """
    Ensure the show's episode pagination has the right page count and page 2
    loads different episodes
    """
    slug = request.node.callspec.params["show"]
    last_page = math.ceil(_episode_count(slug) / PAGINATE)
    pagination = page.locator('.episode-list [aria-label="pagination"]')
    expect(pagination.locator("a", has_text="Last Page")).to_have_attribute(
        "href", re.compile(rf"/show/{slug}/page/{last_page}/$")
    )

    first_card = page.locator(".episode-list .card").nth(0).text_content()
    pagination.locator(".pagination-link", has_text=re.compile(r"^\s*2\s*$")).click()
    page.wait_for_load_state("networkidle")
    assert f"/show/{slug}/page/2" in page.url
    first_card_second_page = page.locator(".episode-list .card").nth(0).text_content()
    assert first_card != first_card_second_page
