#!/usr/bin/env python3
"""Generate llms.txt, llms-full.txt, and per-show llms.txt files.

Runs after `hugo --gc` (see Dockerfile builder stage). Reads the NDJSON
dump Hugo emits at public/llmsdump.json (layout: index.llmsdump.json),
writes the llms files into public/, then the dump is removed.

Output:
  public/llms.txt                    site-wide map (spec: llmstxt.org, v2)
  public/llms-full.txt               core (non-episode) pages concatenated
  public/show/<slug>/llms.txt        per-show episode index (covers /show/<slug>/*)

No third-party dependencies; python 3.8+.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

SITE_BASE = "https://www.jupiterbroadcasting.com"

# One-line blurbs for the root llms.txt; falls back to section description.
SHOW_BLURBS = {
    "linux-unplugged": "Flagship Linux podcast: the latest in Linux desktop, distros, and open source.",
    "linux-action-news": "Weekly short news show covering the biggest stories in Linux and open source.",
    "coder-radio": "Weekly discussion of programming, software development, and the tech industry.",
    "self-hosted": "Two IT guys building and breaking their own self-hosted infrastructure.",
    "this-week-in-bitcoin": "Weekly Bitcoin news, protocol development, and mining updates.",
    "jupiter-extras": "Interviews, Brunch with Brent, and one-off conversations from the JB team.",
    "the-launch": "Jupiter Broadcasting coverage of SpaceX launches.",
    "office-hours": "Listener Q&A and community support episodes.",
}

# Core pages linked from the root llms.txt (path relative to content/, order matters)
CORE_PAGES = [
    ("Membership", "membership/index.md", "How to become a JB member and what perks you get."),
    ("Live", "live/_index.md", "Live show schedule and streaming info."),
    ("Community", "community/_index.md", "Where the JB community gathers (Matrix, Discord, PeerTube, and more)."),
    ("Hosts", "hosts/_index.md", "The people behind the shows."),
    ("Sponsors", "sponsors/_index.md", "Current sponsors."),
    ("Contact", "contact/_index.md", "How to reach the crew (mailbag, picks, feedback)."),
]

EPISODE_STEM_PREFIX = "0"  # episodes are numbered 0001.md .. NNNN.md


def load_dump(dump_path: Path):
    """Parse the NDJSON dump Hugo wrote. Yields one dict per page/section."""
    with dump_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def split_rows(rows):
    """-> (episodes_by_show, sections_by_path, core_pages)"""
    episodes = defaultdict(list)
    sections = {}
    core = []
    for row in rows:
        path = row.get("path") or ""
        parts = path.split("/")
        if row.get("kind") == "section":
            sections[path] = row
        if parts and parts[0] == "show":
            if row.get("kind") == "section" and len(parts) == 2:
                continue  # show section index, kept in `sections`
            stem = Path(path).stem
            if row.get("kind") == "page" and len(parts) == 3 and stem.startswith(EPISODE_STEM_PREFIX):
                episodes[parts[1]].append(row)
            continue
        if row.get("kind") == "page":
            core.append(row)
    for eps in episodes.values():
        eps.sort(key=lambda r: r.get("date") or "", reverse=True)  # newest first
    core.sort(key=lambda r: r.get("path") or "")
    return episodes, sections, core


def episode_line(row):
    title = (row.get("title") or "").strip()
    guests = [g for g in (row.get("guests") or []) if g]
    label = f"{title} (guest: {', '.join(guests)})" if guests else title
    desc = (row.get("desc") or "").strip().replace("\n", " ")
    date = row.get("date") or ""
    url = SITE_BASE + row.get("url", "") + "index.md"
    line = f"- [{date} · {label}]({url})"
    if desc:
        line += f" - {desc}"
    return line


def core_page_url(path):
    """content path -> markdown-twin URL: membership/index.md -> /membership/index.md"""
    base = path
    for leaf in ("_index.md", "index.md"):
        if base.endswith(leaf):
            base = base[: -len(leaf)]
            break
    else:
        if base.endswith(".md"):
            base = base[:-3]
    return f"{SITE_BASE}/{base}index.md"


def root_llms(episodes, sections):
    lines = [
        "# Jupiter Broadcasting",
        "",
        "> Jupiter Broadcasting (JB) is a network of Linux and open source technology podcasts, "
        "including LINUX Unplugged, Linux Action News, Coder Radio, Self-Hosted, and Jupiter EXTRAS. "
        "The site hosts episode show notes plus pages about membership, live shows, sponsors, and community.",
        "",
        "Each show has its own `llms.txt` under its path (e.g. `/show/linux-unplugged/llms.txt`) "
        "listing every episode with its show-notes description. Any page on the site is available "
        "as markdown by appending `index.md` to its URL (e.g. `/show/linux-unplugged/0650/index.md`).",
        "",
        "## Shows",
        "",
    ]
    for slug in sorted(episodes):
        sec = sections.get(f"show/{slug}/_index.md", {})
        name = sec.get("title") or slug
        blurb = SHOW_BLURBS.get(slug) or sec.get("desc") or ""
        lines.append(
            f"- [{name}]({SITE_BASE}/show/{slug}/llms.txt): {len(episodes[slug])} episodes. {blurb}".strip()
        )
    lines += ["", "## Site", ""]
    for name, path, blurb in CORE_PAGES:
        lines.append(f"- [{name}]({core_page_url(path)}): {blurb}")
    lines += [
        "",
        "## Optional",
        "",
        f"- [Archive]({SITE_BASE}/archive/index.md): Legacy shows and old content.",
        f"- [llms-full.txt]({SITE_BASE}/llms-full.txt): All core (non-episode) site pages concatenated.",
    ]
    return "\n".join(lines) + "\n"


def per_show_llms(slug, rows, sections):
    sec = sections.get(f"show/{slug}/_index.md", {})
    title = sec.get("title") or slug
    desc = (sec.get("desc") or SHOW_BLURBS.get(slug) or "").strip()
    lines = [f"# {title}", ""]
    if desc:
        lines += [f"> {desc}", ""]
    lines += [
        f"{len(rows)} episodes of {title} from Jupiter Broadcasting. Newest first. "
        "Each entry links to full markdown show notes: description, episode links, hosts, and guests.",
        "",
        f"## Episodes ({len(rows)})",
        "",
    ]
    lines += [episode_line(r) for r in rows]
    return "\n".join(lines) + "\n"


def llms_full(core, sections):
    parts = [
        "# Jupiter Broadcasting - core site pages (llms-full)",
        "",
        "All non-episode site pages, concatenated. Episode show notes are not included: "
        "each show's episode index lives at /show/<slug>/llms.txt and individual episodes "
        "are markdown at /show/<slug>/<number>/index.md.",
    ]
    for row in core:
        title = (row.get("title") or "").strip()
        body = (row.get("body") or "").strip()
        url = SITE_BASE + row.get("url", "")
        parts.append(f"# {title}\n\nURL: {url}\n\n{body}".strip())
    return "\n\n---\n\n".join(parts) + "\n"


def main(repo_root="."):
    root = Path(repo_root)
    public = root / "public"
    dump = public / "llmsdump.json"
    if not dump.exists():
        sys.exit(f"error: {dump} not found — run `hugo --gc` first")

    episodes, sections, core = split_rows(load_dump(dump))

    (public / "llms.txt").write_text(root_llms(episodes, sections), encoding="utf-8")
    (public / "llms-full.txt").write_text(llms_full(core, sections), encoding="utf-8")
    total_eps = 0
    for slug, rows in episodes.items():
        out_dir = public / "show" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "llms.txt").write_text(per_show_llms(slug, rows, sections), encoding="utf-8")
        total_eps += len(rows)
    print(f"gen_llms: llms.txt + llms-full.txt + {len(episodes)} show indexes ({total_eps} episodes)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
