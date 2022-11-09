import os
import re

from functools import wraps
from typing import List, Any
from pathlib import Path
from pytest import fixture, mark
from playwright.sync_api import Page, FrameLocator, Locator, expect


"""
List of episodes that contain known edge cases
"""
extra_episodes: List[dict] = [
    {
        "show": "linux-unplugged",
        "number": "434"
    },
    {
        "show": "coder-radio",
        "number": "343"
    },
    {
        "show": "self-hosted",
        "number": "59"
    }
]

"""
Cache decorator to reduce repeat computations. Basically if allows long functions to only need to runonly once with a certain set
of parameters. Speed increases are only noticed if the there are no parameters in the function or if the same parameters are being
inputted multiple times.

How it works:
* Check if the cache dictionary has an entry for the function called
* If it doesn't find anything, it runs the function and adds it to the cache.
* If the result is in the cahce, return it instead of running it again
"""
def cache(func) -> Any:
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


"""
Generate list of episode URLS for testing. This list consists of the following
* For each show:
    * 5 oldest episodes
    * 5 newest episodes
* A speified set of episodes that contain "out of the ordinary" things for an episode (an example being a high number of guests
"""
@cache
@fixture()
def episodes() -> List[str]:
    test_episodes: List[str] = []
    shows_dir: str = "content/show"
    meta_files: [str] = ["_index.md", "subscribe.md"]

    # Fist and last 5 episodes
    for show in os.listdir(shows_dir):
        show_url: str = f"/show/{show}"
        episodes: List[str] = [e for e in os.listdir(f"{shows_dir}/{show}") if os.path.isfile(f"{shows_dir}/{show}/{e}") and e not in meta_files]
        episodes.sort()
        # TODO: Check if episode is already in list of urls to test
        for e in episodes[:5] : test_episodes.append(f"{show_url}/{os.path.splitext(e)[0].lstrip('0') or '0'}")
        for e in episodes[-5:] : test_episodes.append(f"{show_url}/{os.path.splitext(e)[0].lstrip('0') or '0'}")

    # extra episodes
    for episode in extra_episodes:
        test_episodes.append(f"/show/{episode['show']}/{episode['number']}")

    return test_episodes


"""
Make sure the title (text in the tab) contains the show name, episode number, and network name (Jupiter Broadcasting)
"""
def test_page_title(page: Page, episodes: List[str]):
    # TODO: See if part of this can be moved to a fixture
    def check_title(page: Page, url: str):
        show, episode_number = url.split('/')[2:4] # This skips the empty string and 'show' in the url
        page.goto(url)
        print(f"{show} - {episode_number}")
        expect(page).to_have_title(re.compile(f".* | {show} {episode_number} | Jupiter Broadcasting"))

    # TODO figure out how to call this loop async
    for url in episodes:
        check_title(page, url)

"""
Test podverse player to and make sure the correct show is displayed
"""
def test_podverse_player(page: Page, episodes: List[str]):
    def check_title(page:Page, url: str):
        show, episode_number = url.split('/')[2:4] # This skips the empty string and 'show' in the url
        page.goto(url)
        pv_player: FrameLocator = page.frame_locator("#pv-embed-player")
        # expect(pv_player).to_be_visible()
        pv_player_show_text: Locator = pv_player.locator(".embed-player-header-top-text").text_content()
        assert pv_player_show_text.replace('-', ' ').lower() == show.replace('-', ' ').lower(), f"Podverse player show for {url} says {pv_player_show_text}"

    # TODO figure out how to call this loop async
    for url in episodes:
        check_title(page, url)
