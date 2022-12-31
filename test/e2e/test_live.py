from time import sleep
from typing import Tuple, Callable
from pytest import mark
from playwright.sync_api import Page


@mark.dev
def test_check_live(
    page: Page,
    set_live: Tuple[Callable, str],
):
    replace_live_event: Callable = set_live[0]
    live_event: str = set_live[1]

    # intercepting reponses for live event
    replace_live_event(page, live_event)

    page.goto('/live')
    sleep(30)
    assert False
