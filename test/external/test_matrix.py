from pytest import mark
from playwright.sync_api import APIRequestContext


"""
Call the matrix federation API to make sure the JB federation is working.
"""
@mark.periodic
def test_matrix_federation(api_request_context: APIRequestContext):
    response = api_request_context.get("https://federationtester.matrix.org/api/report?server_name=jupiterbroadcasting.com")
    assert response.ok, "API did not return a response code of 200-299"
    assert response.body() != "", "API did not return any data"
    assert response.json()["FederationOK"] == True, "Federation is not okay"
