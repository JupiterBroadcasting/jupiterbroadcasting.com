from pytest import mark
from playwright.sync_api import APIRequestContext


@mark.periodic
def test_matrix_federation(api_request_context: APIRequestContext):
    response = api_request_context.get("https://federationtester.matrix.org/api/report?server_name=jupiterbroadcasting.com")
    assert response.json()["FederationOK"] == True
