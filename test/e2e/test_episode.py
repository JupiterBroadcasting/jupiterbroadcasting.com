import os
import re

from typing import List
from pathlib import Path
from pytest import fixture, mark
from playwright.sync_api import Page, expect

"""
List of episodes that contain known edge cases
"""
extra_episodes: List[dict] = [
    {
        "show": "linux-unplugged",
        "number": "434"
    }
]

"""
Generate list of episode URLS for testing. This list consists of the following
* For each show:
    * 5 oldest episodes
    * 5 newest episodes
* A speified set of episodes that contain "out of the ordinary" things for an episode (an example being a high number of guests
"""
@fixture()
def episodes() -> List[str]:
    test_episodes: List[str] = []
    shows_dir: str = "content/show"
    meta_files: [str] = ["_index.md", "subscribe.md"]

    # Fist and last 5 episodes
    for show in os.listdir(shows_dir):
        show_url = f"/show/{show}"
        episodes = [e for e in os.listdir(f"{shows_dir}/{show}") if os.path.isfile(f"{shows_dir}/{show}/{e}") and e not in meta_files]
        episodes.sort()
        for e in episodes[:5] : test_episodes.append(f"{show_url}/{os.path.splitext(e)[0].lstrip('0') or '0'}")
        for e in episodes[-5:] : test_episodes.append(f"{show_url}/{os.path.splitext(e)[0].lstrip('0') or '0'}")

    # extra episodes that are good for testing
    for episode in extra_episodes:
        test_episodes.append(f"/show/{episode['show']}/{episode['number']}")

    return test_episodes


"""
Make sure the title (text in the tab) contains the show name, episode number, and network name (Jupiter Broadcasting)
"""
def test_episode_page_title(page: Page, episodes: List[str]):
    for url in episodes:
        _, show, episode_number = url.partition('/')
        page.goto(url)
        expect(page).to_have_title(re.compile(f".* | {show} {episode_number} | Jupiter Broadcasting"))
