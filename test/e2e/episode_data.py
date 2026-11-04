import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path

CONTENT: Path = Path(__file__).parents[2] / "content"
CONTENT_SHOW: Path = CONTENT / "show"
META_FILES: set[str] = {"_index.md", "subscribe.md"}
ACTIVE_SAMPLE: int = 3
ARCHIVED_SAMPLE: int = 3

EXTRA_EPISODES: list[tuple[str, str]] = [
    ("linux-unplugged", "434"),  # 3 hosts and 3 guests
    ("coder-radio", "343"),  # no sponsors
    ("coder-radio", "443"),  # tag with an apostrophe (issue #534)
]


@dataclass(frozen=True)
class Episode:
    show: str
    number: str
    url: str
    data: dict = field(compare=False, hash=False, repr=False)


def load_episode(path: Path) -> Episode:
    data, _ = json.JSONDecoder().raw_decode(path.read_text().lstrip())
    show = path.parent.name
    number = str(data["episode"])
    return Episode(show=show, number=number, url=f"/show/{show}/{str(data['slug']).lower()}/", data=data)


def _episodes_by_date(show_dir: Path) -> list[Episode]:
    # filenames aren't chronological (e.g. the-launch T-0.md sorts after 0097.md)
    episodes = [load_episode(p) for p in show_dir.glob("*.md") if p.name not in META_FILES]
    return sorted(episodes, key=lambda e: _published(e.data["date"]))


def _published(date: str) -> datetime:
    # Hugo reads dates without an offset as UTC (no timeZone set in config.toml)
    parsed = datetime.fromisoformat(date)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _is_active(show_dir: Path) -> bool:
    return re.search(r"^\s*active\s*=\s*true\b", (show_dir / "_index.md").read_text(), re.M) is not None


def sample_episodes() -> list[Episode]:
    """
    Oldest + newest episodes of every show (ACTIVE_SAMPLE each for active shows, ARCHIVED_SAMPLE for archived),
    plus EXTRA_EPISODES (known edge cases)
    """
    selected: list[Episode] = []
    for show_dir in sorted(p for p in CONTENT_SHOW.iterdir() if p.is_dir()):
        by_date = _episodes_by_date(show_dir)
        n = ACTIVE_SAMPLE if _is_active(show_dir) else ARCHIVED_SAMPLE
        selected += by_date[:n] + by_date[-n:]
    selected += [load_episode(CONTENT_SHOW / show / f"{int(number):04d}.md") for show, number in EXTRA_EPISODES]

    episodes: dict[str, Episode] = {}
    for episode in selected:
        episodes.setdefault(episode.url, episode)
    return list(episodes.values())


def person_type(username: str) -> str | None:
    """
    "host"/"guest" from content/people/<username>.md (YAML front matter), or None if there's no people page
    """
    path = CONTENT / "people" / f"{username}.md"
    if not path.exists():
        return None
    match = re.search(r"^type: *[\"']?(\w+)", path.read_text(), re.M)
    return match.group(1) if match else None


def sponsor_exists(shortname: str) -> bool:
    return (CONTENT / "sponsors" / f"{shortname}.md").exists()
