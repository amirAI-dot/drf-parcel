"""
Wrapping an answer keeps what the view put on it.

If this fails, a header a client reads - a total, a location - or a cookie
the view set disappears the moment the answer is wrapped.
"""

from rest_framework.test import APIClient


def test_a_header_the_view_set_is_still_there(client: APIClient) -> None:
    assert client.get('/explained/')['X-Total'] == '12'


def test_a_cookie_the_view_set_is_still_there(client: APIClient) -> None:
    assert client.get('/explained/').cookies['seen'].value == 'yes'


def test_the_type_is_json(client: APIClient) -> None:
    assert client.get('/explained/')['Content-Type'] == 'application/json'


def test_a_type_the_view_named_itself_is_still_said(client: APIClient) -> None:
    response = client.get('/own-type/')

    assert response['Content-Type'] == 'application/vnd.shop.v2+json'
    assert response.json()['data'] == {'total': 12}
