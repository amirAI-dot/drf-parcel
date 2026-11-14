"""
Every sentence the library says is in its Persian catalogue, and is said in
Persian to a request that asks for it.

If these fail, a Persian-speaking client reads "Deleted." in a toast, or a
sentence added to the code was never translated and nobody noticed.
"""

import ast
import re
from pathlib import Path

import pytest
from django.utils import translation
from rest_framework.test import APIClient

import drf_parcel

SOURCE = Path(drf_parcel.__file__).parent
CATALOGUE = SOURCE / 'locale' / 'fa' / 'LC_MESSAGES' / 'django.po'


def marked_in_the_source() -> set[str]:
    """Every string the library marks with ``_(...)`` - read from the code, not a list."""
    marked: set[str] = set()

    for path in SOURCE.rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == '_'
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                marked.add(node.args[0].value)

    return marked


def in_the_catalogue() -> dict[str, str]:
    """Each msgid of the .po and its msgstr, the header left out."""
    text = CATALOGUE.read_text(encoding='utf-8')
    pairs = re.findall(r'^msgid "(.*)"\nmsgstr "(.*)"$', text, flags=re.MULTILINE)
    return {msgid: msgstr for msgid, msgstr in pairs if msgid}


def test_the_source_marks_what_the_catalogue_was_written_for() -> None:
    marked = marked_in_the_source()

    assert marked, 'no marked string was found: the search itself is broken'
    assert set(in_the_catalogue()) == marked


def test_no_entry_is_left_empty_or_fuzzy() -> None:
    assert all(in_the_catalogue().values())
    assert 'fuzzy' not in CATALOGUE.read_text(encoding='utf-8')


@pytest.mark.parametrize('sentence', sorted(marked_in_the_source()))
def test_the_compiled_catalogue_says_each_sentence_in_persian(sentence: str) -> None:
    """The .mo Django reads agrees with the .po it was compiled from."""
    with translation.override('fa'):
        said = translation.gettext(sentence)

    assert said == in_the_catalogue()[sentence]
    assert said != sentence


def test_a_request_in_persian_is_answered_in_persian(client: APIClient) -> None:
    answer = client.delete('/rings/1/', HTTP_ACCEPT_LANGUAGE='fa').json()

    with translation.override('fa'):
        assert answer['message'] == translation.gettext('Deleted.')
    assert answer['message'] != 'Deleted.'


def test_a_failure_in_persian_is_said_in_persian(client: APIClient) -> None:
    answer = client.get('/fail/bug/', HTTP_ACCEPT_LANGUAGE='fa').json()

    with translation.override('fa'):
        assert answer['message'] == translation.gettext('Something went wrong. Please try again.')


def test_a_request_with_no_language_is_answered_in_the_projects(client: APIClient) -> None:
    assert client.delete('/rings/1/').json()['message'] == 'Deleted.'
