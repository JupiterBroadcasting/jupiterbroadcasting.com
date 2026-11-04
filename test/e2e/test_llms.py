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
    # twin links may be absolute (production) or site-relative (CI/dev)
    m = re.search(r"\]\(((?:https?://[^)]+)?/show/linux-unplugged/\d+/index\.md)\)", r.text)
    assert m, "episode entries must link to markdown twins"
    twin = re.sub(r"^https?://[^/]+", "", m.group(1))
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
    # counts depend on the content snapshot; structure must hold everywhere
    assert data["count"] == len(data["episodes"]) > 0
    for ep in data["episodes"]:
        assert ep["slug"] and ep["title"] and ep["date"] and ep["url"]


def test_prefixed_special_episodes_included(base_url):
    """The-launch 'T-' and office-hours 'p' episodes must be enumerated."""
    data = _get(base_url, "/show/the-launch/episodes.json").json()
    episodes = {e["episode"] for e in data["episodes"]}
    assert "T-0" in episodes and "T-1" in episodes
    assert data["count"] == len(data["episodes"])
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
    # link may be absolute (production) or site-relative (CI/dev); never https-assuming
    assert "/llms-full.txt)" in r


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


def test_show_rss_feed_links(base_url):
    root = _get(base_url, "/llms.txt").text
    shows = root.split("## Shows")[1].split("## Site")[0]
    assert "](https://linuxunplugged.com/rss)" in shows
    optional = root.split("## Optional")[1]
    assert "](https://coder.show/rss)" in optional  # archived shows too
    show_twin = _get(base_url, "/show/linux-unplugged/index.md").text
    assert "RSS feed: [https://linuxunplugged.com/rss]" in show_twin


def test_episode_twin_sponsors_and_transcripts(base_url):
    r = _get(base_url, "/show/linux-unplugged/650/index.md")
    assert r.ok
    assert "Sponsors:" in r.text
    assert "defined.net" in r.text
    assert "Transcripts:" in r.text
    assert ".vtt" in r.text


def test_episodes_json_rich_fields(base_url):
    import json as _json
    r = _get(base_url, "/show/linux-unplugged/episodes.json")
    data = _json.loads(r.text)
    ep = data["episodes"][0]
    assert ep["title"]  # titles, not just slugs
    assert isinstance(ep["hosts"], list)
    assert "guests" in ep and isinstance(ep["guests"], list)
    assert isinstance(ep["transcripts"], list)
    assert ep["transcripts"] and ep["transcripts"][0]["url"].endswith(".vtt")


def test_person_details_on_term_twins(base_url):
    r = _get(base_url, "/hosts/brent/index.md")
    assert r.ok
    assert r.text.startswith("# Brent Gervais")  # real name, not the term slug
    assert "Username: brent" in r.text
    assert "brentgervais.com" in r.text  # bio/homepage rendered, not just episodes
    g = _get(base_url, "/guests/")
    if g.ok:  # guests taxonomy present on this build
        gt = _get(base_url, "/guests/index.md")
        assert gt.ok
        assert "{{" not in gt.text  # no template errors
