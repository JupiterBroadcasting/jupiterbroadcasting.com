import json
import re
from datetime import datetime, timedelta, timezone

from pytest import mark
from playwright.sync_api import Page

from episode_data import CONTENT, CONTENT_SHOW, META_FILES, load_episode

REPO_ROOT = CONTENT.parent
LOOKBACK_DAYS = -int(
    re.search(r"^sponsors\.lookbackdays\s*=\s*(-?\d+)", (REPO_ROOT / "config/_default/params.toml").read_text(), re.M).group(1)
)
# the site may have been built a while before the tests run, so episodes near the cutoff may go either way
CUTOFF_SLACK = timedelta(days=2)


def _sponsor_links() -> dict[str, str]:
    links = {}
    for path in (CONTENT / "sponsors").glob("*.md"):
        text = path.read_text()
        shortname = re.search(r"^shortname:\s*(\S+)", text, re.M)
        link = re.search(r"^link:\s*(\S+)", text, re.M)
        if shortname and link:
            links[shortname.group(1)] = link.group(1)
    return links


SPONSOR_LINKS = _sponsor_links()


def _toml_list(text: str, key: str) -> list[str]:
    match = re.search(rf"^{key}\s*=\s*(\[.*\])", text, re.M)
    return json.loads(match.group(1)) if match else []


def _published(date: str) -> datetime:
    parsed = datetime.fromisoformat(date)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _expected_sections(cutoff: datetime) -> dict[str, set[str]]:
    """
    heading -> sponsor links, per themes/jb/layouts/sponsors/list.html for a build at cutoff + LOOKBACK_DAYS
    """
    sections = {"Jupiter Broadcasting": set(_toml_list((CONTENT / "sponsors/_index.md").read_text(), "sponsors"))}
    for show_dir in sorted(p for p in CONTENT_SHOW.iterdir() if (p / "_index.md").exists()):
        index = (show_dir / "_index.md").read_text()
        recent = {
            sponsor
            for path in show_dir.glob("*.md")
            if path.name not in META_FILES
            for episode in [load_episode(path)]
            if _published(episode.data["date"]) >= cutoff
            for sponsor in episode.data.get("sponsors") or []
        }
        if recent:
            title = re.search(r'^title\s*=\s*"(.*)"', index, re.M).group(1)
            sections[title] = recent | set(_toml_list(index, "sponsors"))
    return {title: {SPONSOR_LINKS[s] for s in sponsors if s in SPONSOR_LINKS} for title, sponsors in sections.items()}


def _rendered_sections(page: Page) -> dict[str, set[str]]:
    return page.evaluate(
        """() => {
            const sections = {};
            let current = null;
            for (const el of document.querySelectorAll('.spnosor-list .content > *')) {
                if (el.tagName === 'H2') sections[current = el.textContent.trim()] = [];
                else if (current) el.querySelectorAll('a[href]').forEach(a => sections[current].push(a.getAttribute('href')));
            }
            return sections;
        }"""
    )


@mark.only_browser("chromium")
def test_sponsors_page(page: Page):
    """
    /sponsors/ lists the network sponsors, then each show with sponsors on an episode in the
    last LOOKBACK_DAYS days (plus the show's own front matter sponsors)
    """
    page.goto("/sponsors/")
    rendered = {title: set(links) for title, links in _rendered_sections(page).items()}
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    required = _expected_sections(cutoff + CUTOFF_SLACK)
    allowed = _expected_sections(cutoff - CUTOFF_SLACK)

    assert set(required) <= set(rendered) <= set(allowed), f"sections: {sorted(rendered)}"
    for title, links in rendered.items():
        assert required.get(title, set()) <= links <= allowed[title], f"{title}: unexpected sponsor links"
