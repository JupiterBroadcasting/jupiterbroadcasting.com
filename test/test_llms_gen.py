"""Unit tests for scripts/gen_llms.py (no site/server needed).

Runs the generator against a fixture NDJSON dump (the format Hugo's
layouts/index.llmsdump.json emits) and validates the llms.txt spec format
of every produced file.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gen_llms  # noqa: E402


def row(kind, path, title, desc="", date="", url=None, body="", guests=(), hosts=(), **extra):
    d = {
        "kind": kind,
        "path": path,
        "url": url if url is not None else "/" + path.replace("_index.md", "").replace("index.md", "").replace(".md", "/"),
        "title": title,
        "desc": desc,
        "date": date,
        "guests": list(guests),
        "hosts": list(hosts),
        "show": "",
        "show_name": "",
        "body": body,
    }
    d.update(extra)
    return d


FIXTURE_ROWS = [
    row("section", "show/_index.md", "Shows", url="/show/"),
    row("section", "show/linux-unplugged/_index.md", "LINUX Unplugged",
        desc="A weekly show about Linux.", url="/show/linux-unplugged/", hosts=["chris", "brent"]),
    row("page", "show/linux-unplugged/0001.md", "Too Much Choice",
        desc="We debate choice.", date="2013-08-12", url="/show/linux-unplugged/0001/",
        hosts=["brent"], show="linux-unplugged", show_name="LINUX Unplugged",
        body="### Episode Links\n\n* [A link](https://example.com)"),
    row("page", "show/linux-unplugged/0650.md", "Nix in the Cold",
        desc="We discuss NixOS.", date="2026-01-13", url="/show/linux-unplugged/0650/",
        guests=["jane"], hosts=["chris", "brent"], show="linux-unplugged",
        show_name="LINUX Unplugged", body="### Episode Links\n\n* [Nix](https://nixos.org)"),
    row("page", "show/jupiter-extras/0006.md", "Brunch with Brent: Chz Bacon",
        desc="A revealing conversation.", date="2019-08-23", url="/show/jupiter-extras/0006/",
        hosts=["brent"], show="jupiter-extras", show_name="Jupiter EXTRAS", body="Notes"),
    row("page", "membership/index.md", "Membership", desc="Support JB",
        url="/membership/", body="## Support Jupiter Broadcasting\nBuy a membership."),
    row("page", "contact/_index.md", "Contact", url="/contact/", body="Reach us."),
]


def build(tmp_path: Path):
    public = tmp_path / "public"
    public.mkdir()
    with (public / "llmsdump.json").open("w", encoding="utf-8") as fh:
        for r in FIXTURE_ROWS:
            fh.write(json.dumps(r) + "\n")
    gen_llms.main(str(tmp_path))
    return public


LINK_RE = re.compile(r"^- \[[^\]]+\]\(https?://[^)]+\)(: .+)?( - .+)?$", re.M)


def validate_root_llms(text: str, section: str = "## Shows", min_links: int = 3):
    lines = text.splitlines()
    assert lines[0].startswith("# "), "H1 site name required first"
    assert any(l.startswith("> ") for l in lines[:6]), "blockquote summary required"
    assert section in text
    links = LINK_RE.findall(text)
    assert len(links) >= min_links, "expected file-list link entries"
    for l in lines:
        if l.startswith("- "):
            assert LINK_RE.match(l), f"malformed file-list entry: {l}"


def test_generates_all_files(tmp_path):
    public = build(tmp_path)
    assert (public / "llms.txt").exists()
    assert (public / "llms-full.txt").exists()
    assert (public / "show/linux-unplugged/llms.txt").exists()
    assert (public / "show/jupiter-extras/llms.txt").exists()


def test_root_llms_spec_format(tmp_path):
    public = build(tmp_path)
    text = (public / "llms.txt").read_text()
    validate_root_llms(text)
    # show entries point at per-show llms.txt and carry episode counts
    assert "](https://www.jupiterbroadcasting.com/show/linux-unplugged/llms.txt): 2 episodes" in text
    # show names come from section front matter titles, not slugs
    assert "[LINUX Unplugged]" in text


def test_per_show_index_newest_first(tmp_path):
    public = build(tmp_path)
    text = (public / "show/linux-unplugged/llms.txt").read_text()
    validate_root_llms(text, section="## Most recent episodes", min_links=3)
    assert "# LINUX Unplugged" in text
    assert "> A weekly show about Linux." in text
    i_new = text.index("Nix in the Cold")
    i_old = text.index("Too Much Choice")
    assert i_new < i_old, "episodes must be newest-first"
    # guest annotation + markdown twin URLs
    assert "Nix in the Cold (guest: jane)" in text
    assert "https://www.jupiterbroadcasting.com/show/linux-unplugged/0650/index.md" in text
    # archive section: range + pattern + episodes.json pointer (full list NOT inlined)
    assert "## Episode archive" in text
    assert "numbered 1-650" in text
    assert "/show/linux-unplugged/<number>/" in text
    assert "/show/linux-unplugged/episodes.json" in text
    epj = json.loads((public / "show/linux-unplugged/episodes.json").read_text())
    assert epj["count"] == 2
    assert {e["number"] for e in epj["episodes"]} == {1, 650}
    assert epj["episodes"][0]["url"].endswith("/show/linux-unplugged/0001/")


def test_recent_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(gen_llms, "RECENT_COUNT", 1)
    public = build(tmp_path)
    text = (public / "show/linux-unplugged/llms.txt").read_text()
    assert "Nix in the Cold" in text
    assert "Too Much Choice" not in text, "only RECENT_COUNT episodes belong in the index"


def test_llms_full_excludes_episodes(tmp_path):
    public = build(tmp_path)
    text = (public / "llms-full.txt").read_text()
    assert "Membership" in text
    assert "Buy a membership." in text
    assert "Too Much Choice" not in text, "episodes must not be inlined in llms-full"
    assert "llmsdump" not in (public / "llms.txt").read_text()
