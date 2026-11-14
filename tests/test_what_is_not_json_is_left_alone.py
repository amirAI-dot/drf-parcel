"""
What is not JSON - and a view that opts out - is never wrapped.

If these fail, a downloaded PDF arrives as an envelope with the file's
bytes in it, or a webhook's caller rejects an answer it did not expect.
"""

from rest_framework.test import APIClient

from tests.conftest import MakeItems


def test_a_plain_django_response_is_left_alone(client: APIClient) -> None:
    response = client.get('/not-json/')

    assert response.content == b'plain text'


def test_a_redirect_is_left_alone(client: APIClient) -> None:
    response = client.post('/not-json/')

    assert response.status_code == 302
    assert response['Location'] == '/elsewhere/'


def test_a_stream_is_left_alone(client: APIClient) -> None:
    response = client.put('/not-json/')

    assert b''.join(response.streaming_content) == b'ab'


def test_a_file_is_left_alone(client: APIClient) -> None:
    response = client.patch('/not-json/')

    assert b''.join(response.streaming_content) == b'%PDF-'


def test_a_list_asked_for_as_csv_stays_csv(client: APIClient) -> None:
    response = client.get('/csv/', HTTP_ACCEPT='text/csv')

    assert response.content == b'1,Ring\n2,Necklace'


def test_the_same_list_asked_for_as_json_is_wrapped(client: APIClient) -> None:
    assert client.get('/csv/').json()['success'] is True


def test_a_view_that_opts_out_answers_its_own_shape(client: APIClient) -> None:
    assert client.post('/webhook/').json() == {'received': True}


def test_a_failure_made_by_hand_is_left_as_it_was_made(client: APIClient) -> None:
    """The error envelope is the exception handler's; a bare failure is not guessed at."""
    response = client.delete('/explained/')

    assert response.status_code == 400
    assert response.json() == {'detail': 'Made by hand.'}


def test_a_page_of_a_view_that_opts_out_is_drfs_own(
    client: APIClient, make_items: MakeItems
) -> None:
    """parcel_wrap = False leaves every answer as DRF gives it - its pages too."""
    make_items(3)

    answer = client.get('/items/opted-out/').json()

    assert set(answer) == {'count', 'next', 'previous', 'results'}
    assert len(answer['results']) == 3


def test_a_feed_of_a_view_that_opts_out_is_drfs_own(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(3)

    assert set(client.get('/feed/opted-out/').json()) == {'next', 'previous', 'results'}
