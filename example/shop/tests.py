"""
What the example shop answers - one test for each thing drf-parcel does in it.

Written with Django's own TestCase, as most projects test, and read as a
client reads: the JSON on the wire.
"""

import logging
from unittest import mock

from django.db import IntegrityError
from django.test import TestCase
from django.utils import translation
from rest_framework.test import APIClient

from shop.models import Order, Product


class TheShopAnswersInOneShape(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.ring = Product.objects.create(name='Ring', price='120.00', stock=4)

    def test_one_product_is_under_data(self) -> None:
        answer = self.client.get(f'/api/products/{self.ring.pk}/').json()

        self.assertEqual(answer['success'], True)
        self.assertEqual(answer['message'], 'Done.')
        self.assertEqual(answer['data']['name'], 'Ring')

    def test_products_come_a_numbered_page_at_a_time(self) -> None:
        for number in range(1, 15):
            Product.objects.create(name=f'Earring {number}', price='40.00')

        answer = self.client.get('/api/products/', {'page': 2}).json()

        self.assertEqual(len(answer['data']), 5)
        self.assertEqual(
            answer['pagination'],
            {
                'type': 'page',
                'count': 15,
                'page': 2,
                'pages': 2,
                'page_size': 10,
                'has_next': False,
                'has_previous': True,
            },
        )

    def test_the_client_chooses_the_page_size_under_the_ceiling(self) -> None:
        for number in range(1, 30):
            Product.objects.create(name=f'Earring {number}', price='40.00')

        asked_five = self.client.get('/api/products/', {'page_size': 5}).json()
        asked_too_many = self.client.get('/api/products/', {'page_size': 500}).json()

        self.assertEqual(asked_five['pagination']['page_size'], 5)
        self.assertEqual(asked_too_many['pagination']['page_size'], 20)

    def test_a_product_added_says_the_views_own_sentence(self) -> None:
        response = self.client.post(
            '/api/products/', {'name': 'Necklace', 'price': '340.00'}, format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'The product was added.')

    def test_a_product_deleted_answers_200_with_the_envelope(self) -> None:
        response = self.client.delete(f'/api/products/{self.ring.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Deleted.')

    def test_an_answer_written_by_hand_is_wrapped_once(self) -> None:
        answer = self.client.post(
            f'/api/products/{self.ring.pk}/restock/', {'quantity': 3}, format='json'
        ).json()

        self.assertEqual(answer['message'], 'The stock was updated.')
        self.assertEqual(answer['data']['stock'], 7)

    def test_the_health_check_keeps_its_own_shape(self) -> None:
        self.assertEqual(self.client.get('/api/health/').json(), {'ok': True})


class OrdersAreAFeed(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.ring = Product.objects.create(name='Ring', price='120.00', stock=100)

    def test_orders_are_read_on_by_cursor_newest_first(self) -> None:
        for _ in range(25):
            placed = self.client.post(
                '/api/orders/', {'product': self.ring.pk, 'quantity': 1}, format='json'
            )
            self.assertEqual(placed.status_code, 201)

        first = self.client.get('/api/orders/').json()
        second = self.client.get(
            '/api/orders/', {'cursor': first['pagination']['next_cursor']}
        ).json()

        self.assertEqual(first['pagination']['type'], 'cursor')
        self.assertEqual(len(first['data']), 10)
        self.assertNotIn(first['data'][-1]['id'], [order['id'] for order in second['data']])


class FailuresAnswerInTheSameShape(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.ring = Product.objects.create(name='Ring', price='120.00', stock=2)

    def test_every_field_that_is_wrong_with_its_code(self) -> None:
        response = self.client.post('/api/orders/', {'quantity': 0}, format='json')

        self.assertEqual(response.status_code, 400)
        answer = response.json()
        self.assertEqual(answer['error_code'], 'validation_error')
        self.assertEqual(
            answer['data']['fields']['product'],
            [{'code': 'required', 'message': 'This field is required.'}],
        )
        self.assertEqual(answer['data']['fields']['quantity'][0]['code'], 'min_value')

    def test_more_than_the_stock_says_how_many_there_are(self) -> None:
        response = self.client.post(
            '/api/orders/', {'product': self.ring.pk, 'quantity': 5}, format='json'
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error_code'], 'out_of_stock')
        self.assertEqual(response.json()['data'], {'available': 2})

    def test_a_product_with_orders_is_not_deleted(self) -> None:
        Order.objects.create(product=self.ring, quantity=1)

        response = self.client.delete(f'/api/products/{self.ring.pk}/')

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['data'], {'orders': 1})
        self.assertTrue(Product.objects.filter(pk=self.ring.pk).exists())

    def test_an_error_written_before_the_library_is_in_the_envelope(self) -> None:
        order = Order.objects.create(product=self.ring, quantity=1)

        response = self.client.get(f'/api/orders/{order.pk}/receipt/')

        self.assertEqual(response.status_code, 402)
        self.assertEqual(response.json()['error_code'], 'payment_required')

    def test_a_name_taken_by_another_request_at_once_is_a_409(self) -> None:
        """The serializer checked it was free; the database refused it a moment later."""
        with mock.patch('rest_framework.validators.UniqueValidator.__call__', return_value=None):
            response = self.client.post(
                '/api/products/', {'name': 'Ring', 'price': '1.00'}, format='json'
            )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error_code'], 'already_exists')

    def test_a_bug_says_nothing_and_is_reported(self) -> None:
        with (
            mock.patch('shop.services.delete_product', side_effect=IntegrityError('nope')),
            self.assertLogs('shop.bugs', level=logging.WARNING),
            self.assertLogs('drf_parcel', level=logging.ERROR),
        ):
            response = self.client.delete(f'/api/products/{self.ring.pk}/')

        self.assertEqual(response.status_code, 500)
        self.assertNotIn('nope', response.content.decode())

    def test_a_request_in_persian_is_answered_in_persian(self) -> None:
        answer = self.client.get(f'/api/products/{self.ring.pk}/', HTTP_ACCEPT_LANGUAGE='fa').json()

        with translation.override('fa'):
            self.assertEqual(answer['message'], translation.gettext('Done.'))


class TheSchemaSaysTheEnvelope(TestCase):
    def test_the_schema_describes_what_arrives(self) -> None:
        schema = self.client.get('/api/schema/', {'format': 'json'}).json()

        product = schema['paths']['/api/products/{id}/']['get']['responses']['200']
        body = product['content']['application/json']['schema']
        self.assertIn('data', body['properties'])
        self.assertIn('ErrorEnvelope', schema['components']['schemas'])
