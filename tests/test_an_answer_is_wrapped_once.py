"""
An answer already in the envelope is never wrapped again.

If this fails, a client finds ``data.data.total``.
"""

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory

from tests.project.views import RingViewSet


class LookalikeViewSet(RingViewSet):
    """A view whose own payload happens to share the envelope's keys."""

    def list(self, request: Request) -> Response:
        return Response({'success': True, 'status_code': 200, 'mine': 1})


def test_an_explicit_success_is_not_wrapped_twice(client: APIClient) -> None:
    assert client.get('/totals/').json()['data'] == {'total': 12}


def test_an_explicit_failure_is_not_wrapped_and_keeps_its_parts(client: APIClient) -> None:
    response = client.post('/explained/')

    assert response.status_code == 409
    assert response.json() == {
        'success': False,
        'status_code': 409,
        'message': 'This province has branches and cannot be deleted.',
        'data': {'branches': 3},
        'error_code': 'province_in_use',
    }


def test_a_payload_that_looks_like_an_envelope_is_still_a_payload() -> None:
    """Being in the envelope is said by the response's class, never guessed from keys."""
    request = APIRequestFactory().get('/')
    response = LookalikeViewSet.as_view({'get': 'list'})(request)
    response.render()

    assert response.data['data'] == {'success': True, 'status_code': 200, 'mine': 1}
