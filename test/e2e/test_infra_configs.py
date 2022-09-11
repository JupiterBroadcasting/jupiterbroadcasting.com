from json import loads as j_loads
from pytest import mark
from playwright.sync_api import Page

@mark.skip(reason="currently failing, and troubleshooting in #383")
def test_matrix_well_known(page: Page):
    contents = page.goto("/.well-known/matrix/server").text()
    
    well_known_structure = {
        "m.server": "colony.jupiterbroadcasting.com:443"
    }

    if j_loads(contents) == well_known_structure:
        assert True
    else:
        assert False
