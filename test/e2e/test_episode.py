import re

from pytest import mark, param
from playwright.sync_api import APIRequestContext, Locator, Page, expect

from episode_data import CONTENT_SHOW, Episode, has_podverse, is_active, person_type, sample_episodes, sponsor_exists

SAMPLE_EPISODES: list[Episode] = sample_episodes()


def episode_params():
    return mark.parametrize("ep", [param(e, id=e.url, marks=mark.episodes) for e in SAMPLE_EPISODES])


def test_sample_episodes_shape():
    """
    Sample has no duplicates, covers every show, and includes the hand-picked edge cases
    """
    urls = [e.url for e in SAMPLE_EPISODES]
    assert len(set(urls)) == len(urls)
    assert "/show/linux-unplugged/434/" in urls
    assert {e.show for e in SAMPLE_EPISODES} == {p.name for p in CONTENT_SHOW.iterdir() if p.is_dir()}


@mark.only_browser("chromium")
@episode_params()
def test_episode_page_title(page: Page, ep: Episode):
    """
    Tab title is "<title> | <show> <number> | Jupiter Broadcasting", or "<show> <number> | Jupiter Broadcasting"
    when the episode title is just the show name and number (themes/jb/layouts/partials/meta.html)
    """
    page.goto(ep.url, wait_until="domcontentloaded")
    show_and_number = re.escape(f"{ep.data['show_name']} {ep.number}")
    expect(page).to_have_title(re.compile(rf"^(.+ \| )?{show_and_number} \| Jupiter Broadcasting$"))


@mark.only_browser("chromium")
@episode_params()
def test_episode_player(page: Page, ep: Episode):
    """
    Podverse embed for episodes with a podcast_file in a show with a Podverse ID, otherwise a plain <audio> player
    """
    page.goto(ep.url, wait_until="domcontentloaded")
    show_dir = CONTENT_SHOW / ep.show
    has_audio = any(ep.data.get(k) for k in ("podcast_file", "podcast_ogg_file", "podcast_alt_file"))
    if ep.data.get("podcast_file") and has_podverse(show_dir):
        player = page.locator("#pv-embed-player")
        expect(player).to_be_attached()
        expect(player).to_have_attribute("src", re.compile(re.escape(ep.data["episode_guid"])))
    elif has_audio or is_active(show_dir):
        expect(page.locator("audio source")).not_to_have_count(0)
    else:
        expect(page.locator("audio source")).to_have_count(0)


@mark.only_browser("chromium")
@episode_params()
def test_episode_support_subscribe(page: Page, ep: Episode):
    page.goto(ep.url, wait_until="domcontentloaded")
    expect(page.locator("a.button", has_text="Support")).to_have_attribute("href", re.compile(r"/membership/$"))
    subscribe = page.locator("a.button", has_text="Subscribe to")
    if is_active(CONTENT_SHOW / ep.show) or (CONTENT_SHOW / ep.show / "subscribe.md").exists():
        expect(subscribe).to_be_visible()
    else:
        expect(subscribe).to_have_count(0)


@mark.only_browser("chromium")
@episode_params()
def test_episode_header_image(page: Page, ep: Episode):
    page.goto(ep.url, wait_until="domcontentloaded")
    expect(page.locator(f'img[src="{ep.data["header_image"]}"]')).to_be_visible()


def _people_column(page: Page, heading: str) -> Locator:
    return page.locator(".hosts > .column").filter(has=page.locator(f'h2:text-is("{heading}")'))


def _expected_people_hrefs(usernames: list[str]) -> list[str]:
    # template silently skips usernames without a people page, and links by the person's type, not the role
    return [f"/{person_type(u)}s/{u}/" for u in usernames if person_type(u)]


@mark.only_browser("chromium")
@episode_params()
def test_episode_hosts_guests(page: Page, ep: Episode):
    page.goto(ep.url, wait_until="domcontentloaded")
    for heading, key in (("Hosts", "hosts"), ("Guests", "guests")):
        expected = _expected_people_hrefs(ep.data.get(key) or [])
        column = _people_column(page, heading)
        if key == "guests" and not ep.data.get("guests"):
            expect(column).to_have_count(0)
            continue
        links = column.locator("a[href]")
        assert [links.nth(i).get_attribute("href") for i in range(links.count())] == expected


@mark.only_browser("chromium")
@episode_params()
def test_episode_sponsors(page: Page, ep: Episode):
    """
    Sponsors render in a mobile and a desktop block; only the visible one is counted
    """
    page.goto(ep.url, wait_until="domcontentloaded")
    expected = [s for s in ep.data.get("sponsors") or [] if sponsor_exists(s)]
    sponsor_list = page.locator(".sponsor-list:visible")
    if not ep.data.get("sponsors"):
        expect(page.locator('h2:text-is("Sponsors")')).to_have_count(0)
        return
    expect(sponsor_list).to_have_count(1)
    expect(sponsor_list.locator(".card")).to_have_count(len(expected))


@mark.only_browser("chromium")
@episode_params()
def test_episode_tags(page: Page, ep: Episode, api_request_context: APIRequestContext):
    """
    Every front matter tag is shown, and its tag page exists (covers spaces and apostrophes, issue #534)
    """
    page.goto(ep.url, wait_until="domcontentloaded")
    tags = page.locator(".tags .tag a")
    assert sorted(t.strip() for t in tags.all_text_contents()) == sorted(ep.data.get("tags") or [])
    broken = [href for href in (tags.nth(i).get_attribute("href") for i in range(tags.count()))
              if not api_request_context.get(href).ok]
    assert broken == []


@mark.only_browser("chromium")
@episode_params()
def test_episode_links(page: Page, ep: Episode, api_request_context: APIRequestContext):
    """
    Links in the episode body have an href, and same-site ones resolve. External links are not fetched.
    """
    page.goto(ep.url, wait_until="domcontentloaded")
    hrefs = page.locator(".tile.is-parent.is-8 > .tile.is-child:last-child a").evaluate_all(
        "els => els.map(e => e.getAttribute('href'))"
    )
    assert all(hrefs), f"empty href in {hrefs}"
    internal = [h for h in hrefs if h.startswith("/") and not h.startswith("//")]
    assert [h for h in internal if not api_request_context.get(h).ok] == []


def test_episode_lup434_all_browsers(page: Page):
    """
    One known-rich episode (3 hosts, 3 guests, sponsors) on every browser
    """
    page.goto("/show/linux-unplugged/434/", wait_until="domcontentloaded")
    expect(page.locator("#pv-embed-player")).to_be_attached()
    expect(_people_column(page, "Hosts").locator("a[href]")).to_have_count(3)
    expect(_people_column(page, "Guests").locator("a[href]")).to_have_count(3)
    expect(page.locator(".sponsor-list:visible .card")).not_to_have_count(0)


@mark.skip("Issue #516")
def test_episode_emoji_tags():
    """
    Emoji tags render a tag page. No sample episode has emoji tags today; add one when #516 is fixed.
    """
