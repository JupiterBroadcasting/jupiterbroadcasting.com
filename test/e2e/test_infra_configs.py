from playwright.sync_api import APIRequestContext


def test_matrix_well_known(
    api_request_context: APIRequestContext,
):
    """
    Check to make sure the files required for matrix federation and name resolution
    are present and contain necessary details
    """
    well_known_folder = "/.well-known/matrix"
    well_known_types = {
        "client": {
            "m.homeserver": {"base_url": "https://colony.jupiterbroadcasting.com"}
        },
        "server": {"m.server": "colony.jupiterbroadcasting.com:443"},
    }

    for well_known_key, well_known_data in well_known_types.items():
        response = api_request_context.get(f"{well_known_folder}/{well_known_key}")

        assert response.ok, "200-299 status code"
        assert response.body() != "", "response is not empty"
        assert response.json() == well_known_data, "expected reponse for JB matrix"
