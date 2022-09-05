from playwright.sync_api import APIRequestContext


def test_matrix_well_known(
    api_request_context: APIRequestContext,
):
    well_known_path = "/.well-known/matrix/server"
    response = api_request_context.get(well_known_path)

    assert response.ok, "200-299 status code"
    assert response.body() != "", "response is not empty"
    assert response.json() == {
        "m.server": "colony.jupiterbroadcasting.com:443"
    }, "expected reponse for JB matrix"
