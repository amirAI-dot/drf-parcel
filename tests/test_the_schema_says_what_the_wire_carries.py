"""
The generated OpenAPI document describes what a client receives - the
envelope - and not only what is inside it.

If these fail, a frontend that generates its types from the schema writes
``response.id`` where the truth is ``response.data.id``, offers a page size
the server ignores, or knows nothing of the shape a failure arrives in.
"""

from typing import Any

import pytest
from django.test import override_settings
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema

from tests.project import documented

Schema = dict[str, Any]


def generate() -> Schema:
    schema: Schema = SchemaGenerator(patterns=documented.urlpatterns).get_schema(
        request=None, public=True
    )
    return schema


@pytest.fixture
def schema() -> Schema:
    return generate()


def component(schema: Schema, reference: Schema) -> Schema:
    name = reference['$ref'].rsplit('/', 1)[-1]
    found: Schema = schema['components']['schemas'][name]
    return found


def body(schema: Schema, path: str, method: str, code: str) -> Schema:
    found: Schema = schema['paths'][path][method]['responses'][code]['content']['application/json'][
        'schema'
    ]
    return found


def parameters(schema: Schema, path: str) -> dict[str, Schema]:
    return {found['name']: found for found in schema['paths'][path]['get'].get('parameters', [])}


def test_the_document_is_valid_openapi(schema: Schema) -> None:
    validate_schema(schema)


def test_one_object_is_under_data(schema: Schema) -> None:
    answer = body(schema, '/items/{id}/', 'get', '200')

    assert answer['required'] == ['success', 'status_code', 'message', 'data']
    assert answer['properties']['success']['example'] is True
    assert answer['properties']['data'] == {'$ref': '#/components/schemas/Item'}


def test_a_created_object_is_under_data(schema: Schema) -> None:
    answer = body(schema, '/items/', 'post', '201')

    assert answer['properties']['data'] == {'$ref': '#/components/schemas/Item'}


def test_a_delete_is_a_200_with_a_body(schema: Schema) -> None:
    responses = schema['paths']['/items/{id}/']['delete']['responses']

    assert '204' not in responses
    assert body(schema, '/items/{id}/', 'delete', '200')['properties']['data'] == {'type': 'object'}


def test_a_numbered_page_is_its_own_envelope(schema: Schema) -> None:
    page = component(schema, body(schema, '/items/', 'get', '200'))

    assert page['properties']['data'] == {
        'type': 'array',
        'items': {'$ref': '#/components/schemas/Item'},
    }
    assert page['properties']['pagination']['properties']['type']['example'] == 'page'
    assert 'pagination' in page['required']


def test_a_feed_is_its_own_envelope_under_its_own_name(schema: Schema) -> None:
    reference = body(schema, '/feed/', 'get', '200')
    feed = component(schema, reference)

    assert reference['$ref'].endswith('/ItemCursorPage')
    assert feed['properties']['pagination']['properties']['type']['example'] == 'cursor'


def test_a_page_in_a_view_without_the_mixin_is_still_its_envelope(schema: Schema) -> None:
    page = component(schema, body(schema, '/plain-list/', 'get', '200'))

    assert 'pagination' in page['properties']


def test_a_page_described_inline_is_not_wrapped_twice(schema: Schema) -> None:
    page = body(schema, '/loose/', 'get', '200')

    assert 'pagination' in page['properties']
    assert page['properties']['data']['type'] == 'array'


def test_a_numbered_page_is_named_for_what_it_is(schema: Schema) -> None:
    assert body(schema, '/items/', 'get', '200') == {'$ref': '#/components/schemas/ItemPage'}


def test_a_page_by_drfs_own_paginator_is_wrapped_like_any_answer(schema: Schema) -> None:
    answer = body(schema, '/drf-paged/', 'get', '200')

    assert answer['properties']['data'] == {'$ref': '#/components/schemas/PaginatedItemList'}
    assert 'results' in component(schema, answer['properties']['data'])['properties']


def test_a_page_of_a_view_that_opts_out_is_described_as_drfs(schema: Schema) -> None:
    for path in ('/opted-out-list/', '/opted-out-feed/'):
        page = component(schema, body(schema, path, 'get', '200'))

        assert 'results' in page['properties'], path
        assert 'success' not in page['properties'], path


def test_a_page_named_outside_an_operation_does_not_break() -> None:
    """drf-spectacular may name a page before, or without, describing an operation."""
    from drf_parcel.schema import ParcelAutoSchema
    from tests.project.shelf.views import ItemList

    described = ParcelAutoSchema()
    described.view = ItemList()

    assert described.get_paginated_name('Item') == 'ItemPage'


def test_page_size_only_where_the_client_may_choose_it(schema: Schema) -> None:
    assert 'page_size' not in parameters(schema, '/items/')
    assert 'page' in parameters(schema, '/items/')

    sized = parameters(schema, '/sized/')['page_size']['schema']
    assert (sized['minimum'], sized['maximum']) == (1, 5)

    feed = parameters(schema, '/feed/')
    assert 'cursor' in feed
    assert feed['page_size']['schema']['maximum'] == 3


def test_a_view_without_the_mixin_is_described_as_it_answers(schema: Schema) -> None:
    assert body(schema, '/plain/{id}/', 'get', '200') == {'$ref': '#/components/schemas/Item'}


def test_a_view_that_opts_out_is_described_as_it_answers(schema: Schema) -> None:
    assert body(schema, '/opted-out/{id}/', 'get', '200') == {'$ref': '#/components/schemas/Item'}


def test_only_the_json_answer_is_wrapped(schema: Schema) -> None:
    content = schema['paths']['/csv/']['get']['responses']['200']['content']

    assert 'success' in content['application/json']['schema']['properties']
    assert 'success' not in content['text/csv']['schema'].get('properties', {})


def test_a_success_documented_with_no_body_is_still_an_envelope(schema: Schema) -> None:
    assert body(schema, '/silent/', 'get', '200')['properties']['data'] == {'type': 'object'}


def test_a_hidden_view_stays_hidden(schema: Schema) -> None:
    assert '/hidden/{id}/' not in schema['paths']


def test_every_operation_fails_in_the_error_envelope(schema: Schema) -> None:
    for path, operations in schema['paths'].items():
        for method, operation in operations.items():
            reference = operation['responses']['default']['content']['application/json']
            assert reference['schema'] == {'$ref': '#/components/schemas/ErrorEnvelope'}, (
                path,
                method,
            )

    error = schema['components']['schemas']['ErrorEnvelope']
    assert error['properties']['success']['example'] is False
    assert 'error_code' in error['required']


def test_an_operation_that_takes_a_body_documents_its_validation_error(schema: Schema) -> None:
    assert body(schema, '/items/', 'post', '400') == {
        '$ref': '#/components/schemas/ValidationErrorEnvelope'
    }
    assert '400' not in schema['paths']['/items/']['get']['responses']

    fields = schema['components']['schemas']['ValidationErrorEnvelope']['properties']['data'][
        'properties'
    ]['fields']
    assert fields['additionalProperties']['items']['required'] == ['code', 'message']


def test_a_failure_the_view_documents_itself_is_kept(schema: Schema) -> None:
    response = schema['paths']['/own-failure/']['post']['responses']['400']

    assert response['description'] == 'Our own.'


@override_settings(DRF_PARCEL={'FIELD_ERRORS': 'messages'})
def test_field_errors_as_messages_are_described_as_text() -> None:
    fields = generate()['components']['schemas']['ValidationErrorEnvelope']['properties']['data'][
        'properties'
    ]['fields']

    assert fields['additionalProperties']['items'] == {'type': 'string'}


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
        'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
        'EXCEPTION_HANDLER': 'tests.project.handlers.project_exception_handler',
    }
)
def test_a_projects_own_handler_built_on_the_librarys_is_recognised() -> None:
    """A handler that calls the library's and says so with functools.wraps."""
    assert 'ErrorEnvelope' in generate()['components']['schemas']


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
        'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
    }
)
def test_without_the_librarys_handler_no_error_envelope_is_promised() -> None:
    schema = generate()

    assert 'ErrorEnvelope' not in schema['components']['schemas']
    assert 'default' not in schema['paths']['/items/']['get']['responses']
