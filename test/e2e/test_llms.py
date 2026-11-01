"""E2E checks for the llms.txt machinery (Hugo-native output formats).

Pure-HTTP tests (no browser needed), consistent with the llmstxt.org v2 contract:
  - /llms.txt at root, text/plain, spec structure
  - /llms-full.txt core pages, front-matter-free markdown
  - per-show llms.txt (curated) + episodes.json (full enumeration)
  - markdown twins at <url>index.md, incl. prefixed special episodes
  - discovery links (describedby / alternate) in HTML heads

Run: pytest test/e2e/test_llms.py --base-url http://127.0.0.1:18080
"""
import re

import pytest

requests = pytest.importorskip("requests")


def _get(base_url, path):
    return requests.get(base_url.rstrip("/") + path, timeout=30)


def test_root_llms_txt(base_url):
    r = _get(base_url, "/llms.txt")
    assert r.ok
    assert r.headers["content-type"].startswith("text/plain")
    assert "Jupiter Broadcasting" in r.text
    assert "## Shows" in r.text
    assert "/show/linux-unplugged/llms.txt" in r.text


def test_llms_full_txt(base_url):
    r = _get(base_url, "/llms-full.txt")
    assert r.ok
    assert r.headers["content-type"].startswith("text/plain")
    assert "Membership" in r.text
    assert "+++" not in r.text  # front matter stripped


def test_per_show_llms_and_markdown_twins(base_url):
    r = _get(base_url, "/show/linux-unplugged/llms.txt")
    assert r.ok
    assert r.headers["content-type"].startswith("text/plain")
    assert "## Most recent episodes" in r.text
    assert "## Episode archive" in r.text
    # curated file stays small: full enumeration lives in episodes.json
    assert len(r.text) < 20_000, "per-show llms.txt should be curated, not a full index"
    assert "/show/linux-unplugged/episodes.json" in r.text
    m = re.search(r"\]\((https?://[^)]+/show/linux-unplugged/\d+/index\.md)\)", r.text)
    assert m, "episode entries must link to markdown twins"
    twin = m.group(1).replace("https://www.jupiterbroadcasting.com", "")
    t = _get(base_url, twin)
    assert t.ok
    assert "URL:" in t.text


def test_llms_not_rendered_on_non_show_sections(base_url):
    # outputs are enabled per-show in front matter, not site-wide sections
    assert not _get(base_url, "/show/llms.txt").ok
    assert not _get(base_url, "/hosts/llms.txt").ok
    assert not _get(base_url, "/guests/llms.txt").ok


def test_episodes_json(base_url):
    r = _get(base_url, "/show/linux-unplugged/episodes.json")
    assert r.ok
    assert r.headers["content-type"].startswith("application/json")
    data = r.json()
    assert data["count"] == len(data["episodes"]) == 650
    assert data["episodes"][0]["slug"] == "650"
    assert "/show/linux-unplugged/650/" in data["episodes"][0]["url"]


def test_prefixed_special_episodes_included(base_url):
    """The-launch 'T-' and office-hours 'p' episodes must be enumerated."""
    data = _get(base_url, "/show/the-launch/episodes.json").json()
    episodes = {e["episode"] for e in data["episodes"]}
    assert "T-0" in episodes and "T-1" in episodes
    assert data["count"] == 53  # 50 numbered + 3 T- specials
    data = _get(base_url, "/show/office-hours/episodes.json").json()
    assert any(str(e["episode"]).startswith("p") for e in data["episodes"])


def test_episode_markdown_twins(base_url):
    assert _get(base_url, "/show/linux-unplugged/650/index.md").ok
    r = _get(base_url, "/show/the-launch/t-2/index.md")
    assert r.ok  # prefixed slug twin resolves at its lowercase permalink
    r = _get(base_url, "/community/index.md")
    assert r.ok
    assert "+++" not in r.text  # twin is front-matter-free markdown


def test_discovery_links_on_html_pages(base_url):
    r = _get(base_url, "/")
    assert 'rel="describedby"' in r.text
    assert "/llms.txt" in r.text
    r = _get(base_url, "/show/linux-unplugged/")
    assert 'rel="describedby"' in r.text
    assert "/show/linux-unplugged/llms.txt" in r.text


def test_root_shows_active_archived_split(base_url):
    r = _get(base_url, "/llms.txt").text
    shows = r.split("## Shows")[1].split("## Site")[0]
    assert "LINUX Unplugged" in shows
    assert "Coder Radio" not in shows  # archived: not in nav, not in ## Shows
    optional = r.split("## Optional")[1]
    assert "Coder Radio" in optional and "Self-Hosted" in optional
    # llms-full link is absolute like every other link
    assert "](https://www.jupiterbroadcasting.com/llms-full.txt)" in r


def test_hosts_twin_lists_hosts(base_url):
    r = _get(base_url, "/hosts/index.md")
    assert r.ok
    for h in ("brent", "chris", "wes"):
        assert f"/hosts/{h}/index.md" in r.text
    # individual host term twin lists episodes
    r = _get(base_url, "/hosts/brent/index.md")
    assert r.ok
    assert "/show/" in r.text
    # people twin carries front-matter facts, not just a slug
    r = _get(base_url, "/people/brent/index.md")
    assert r.ok
    assert "brentgervais.com" in r.text
    assert "Username: brent" in r.text


def test_llms_full_no_leaked_yaml_frontmatter(base_url):
    r = _get(base_url, "/llms-full.txt").text
    assert "avatar_small" not in r  # YAML front matter stripped
    assert "&#43;" not in r and "&amp;" not in r  # no HTML escaping in text output
    assert "Brent Gervais" in r
