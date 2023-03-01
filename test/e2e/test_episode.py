import os
import re

from pytest import fixture, mark
from playwright.sync_api import Page, FrameLocator, expect


"""
Dictionary of episodes that contain known edge cases
"""
EXTRA_EPISODES: list[dict[str, str]] = [
    {  # 3 Hosts and 3 Guests
        "show": "linux-unplugged",
        "number": "434"
    },
    {  # No Sponsor
        "show": "coder-radio",
        "number": "343"
    }
]


@fixture()
def episodes() -> list[str]:
    """
    Generate list of episode URLS for testing. This list consists of the following
    * For each show:
        * 5 oldest episodes
        * 5 newest episodes
    * A specified set of episodes that contain "out of the ordinary" things for an episode (an example being a high number of guests
    """
    test_episodes: list[str] = []
    shows_dir: str = "content/show"
    meta_files: [str] = ["_index.md", "subscribe.md"]

    # Fist and last 5 episodes for each show
    for show in os.listdir(shows_dir):
        show_url: str = f"/show/{show}"
        all_episodes: list[str] = [e for e in os.listdir(f"{shows_dir}/{show}") if os.path.isfile(f"{shows_dir}/{show}/{e}") and e not in meta_files]
        all_episodes.sort()

        test_episodes += [f"{show_url}/{os.path.splitext(e)[0].lstrip('0') or '0'}" for e in all_episodes[:5:] if e not in test_episodes]  # First 5 episodes of a show
        test_episodes += [f"{show_url}/{os.path.splitext(e)[0].lstrip('0') or '0'}" for e in all_episodes[-5::] if e not in test_episodes]  # 5 most recent episodes of a show

    # Defined list of edge case episodes
    test_episodes += [f"/show/{e['show']}/{e['number']}" for e in EXTRA_EPISODES if e not in test_episodes]

    return test_episodes


@mark.dev
def test_page_title(page: Page, episodes: list[str]):
    """
    Make sure the title (text in the tab) contains the show name, episode number, and
    network name (Jupiter Broadcasting)
    """
    # TODO figure out how to call this loop async
    for url in episodes:
        show, episode_number = url.split('/')[2:4] # This skips the empty string and 'show' in the url
        page.goto(url)
        print(f"{show} - {episode_number}")
        expect(page).to_have_title(re.compile(f".* | {show} {episode_number} | Jupiter Broadcasting"))


def test_podverse_player(page: Page, episodes: list[str]):
    """
    Test podverse player to and make sure the correct show is displayed
    """
    def check_title(page: Page, url: str):
        show, episode_number = url.split('/')[2:4]  # This skips the empty string and 'show' in the url
        page.goto(url)
        pv_player: FrameLocator = page.frame_locator("#pv-embed-player")
        # expect(pv_player).to_be_visible()
        pv_player_show_text: str = pv_player.locator(".embed-player-header-top-text").text_content()
        assert pv_player_show_text.replace('-', ' ').lower() == show.replace('-', ' ').lower(), \
            f"Podverse player show for {url} says {pv_player_show_text}"

    # TODO figure out how to call this loop async
    for url in episodes:
        check_title(page, url)


def test_tag_broken_link_spaces(page: Page):
    """
    Checking for broken tag links with spaces in them
    """
    page.goto("/show/linux-unplugged/489/")
    page.locator(".tag > a", has_text="linux unplugged").click()
    expect(page.locator(".title", has_text="Tag: linux unplugged")).to_be_visible()
