"""Views that fail, one way each - every kind of failure a real view meets."""

from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_parcel.exceptions import DomainError
from drf_parcel.responses import EnvelopeMixin, error_response
from tests.project.shelf.models import Item, Tag


class ProvinceInUseError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')


class LegacyError(exceptions.APIException):
    """An error a project wrote before the library: DRF's own base, no data."""

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_code = 'payment_required'
    default_detail = 'Pay first.'


class LegacyWithDataError(LegacyError):
    def __init__(self) -> None:
        super().__init__()
        self.data = {'amount': 12}


class NamelessError(LegacyError):
    """An error whose class names no code at all."""

    default_code = ''


def raise_secret() -> None:
    raise RuntimeError('SELECT * FROM patients WHERE phone = 09120000000')


FAILURES: dict[str, Any] = {
    'domain': lambda: ProvinceInUseError(data={'branches': 3}),
    'domain-message': lambda: ProvinceInUseError(
        _('Move its 3 branches first.'), data={'branches': 3}
    ),
    'domain-code': lambda: ProvinceInUseError(code='province_locked'),
    'legacy': LegacyError,
    'legacy-data': LegacyWithDataError,
    'legacy-dict': lambda: LegacyError({'amount': ['Too little.']}),
    'legacy-empty': lambda: LegacyError([]),
    'legacy-nameless': NamelessError,
    'refused-as-invalid': lambda: exceptions.PermissionDenied(
        'Your account is not valid for this.', code='invalid'
    ),
    'http404': lambda: Http404('No Patient matches the given query.'),
    'django-permission': DjangoPermissionDenied,
    'drf-permission': exceptions.PermissionDenied,
    'django-permission-message': lambda: DjangoPermissionDenied(
        'You may only edit your own orders.'
    ),
    'django-validation': lambda: DjangoValidationError(
        {'phone': [DjangoValidationError('Enter a valid phone number.', code='invalid')]}
    ),
    'django-validation-plain': lambda: DjangoValidationError('The dates are the wrong way round.'),
    # What a model's full_clean() raises when its clean() refuses: Django's own key.
    'django-validation-model': lambda: DjangoValidationError(
        {
            '__all__': [DjangoValidationError('The dates are the wrong way round.')],
            'phone': [DjangoValidationError('Enter a valid phone number.', code='invalid')],
        }
    ),
    'empty-validation': lambda: exceptions.ValidationError({}),
    # The shape DRF before 3.18 gives a list of records: one entry per record, empty if valid.
    'list-validation': lambda: exceptions.ValidationError(
        [{}, {'name': [exceptions.ErrorDetail('This field is required.', code='required')]}]
    ),
    'throttled': lambda: exceptions.Throttled(wait=12.7),
    'throttled-no-wait': exceptions.Throttled,
    'bug': raise_secret,
    'write-then-fail': lambda: (
        Item.objects.create(name='half a write', created_at='2026-01-01T00:00:00Z'),
        ProvinceInUseError(),
    )[1],
}


class FailingView(EnvelopeMixin, APIView):
    """GET /fail/<how>/ raises the failure named."""

    def get(self, request: Request, how: str) -> Response:
        made = FAILURES[how]()

        if isinstance(made, BaseException):
            raise made

        return Response()


class RefusedByHandView(EnvelopeMixin, APIView):
    """POST writes, then answers a failure by returning it rather than raising it."""

    def post(self, request: Request) -> Response:
        Item.objects.create(name='half a write', created_at='2026-01-01T00:00:00Z')
        return error_response(
            message=_('This province has branches and cannot be deleted.'),
            error_code='province_in_use',
            status_code=status.HTTP_409_CONFLICT,
        )


class LineSerializer(serializers.Serializer[Any]):
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(max_length=5)
    items = LineSerializer(many=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs['name'] == 'late':
            raise serializers.ValidationError('The dates are the wrong way round.')
        return attrs


class OrderView(EnvelopeMixin, APIView):
    """POST an order: every way input can be wrong, from a serializer."""

    def post(self, request: Request) -> Response:
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class ManyOrdersView(EnvelopeMixin, APIView):
    """POST a list of orders, validated as one."""

    def post(self, request: Request) -> Response:
        serializer = OrderSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class SignedInView(EnvelopeMixin, APIView):
    """A view only somebody signed in may read, by HTTP Basic."""

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        return Response({'secret': True})


class TagView(EnvelopeMixin, APIView):
    """POST writes to the database without asking first - for its constraints to refuse."""

    def post(self, request: Request) -> Response:
        Tag.objects.create(name='taken')
        Tag.objects.create(name='taken')
        return Response()

    def put(self, request: Request) -> Response:
        Item.objects.create(name=None, created_at=None)
        return Response()


class ReadOnlyView(EnvelopeMixin, APIView):
    """A view that reads only GET, and parses what it is sent on PUT."""

    def get(self, request: Request) -> Response:
        return Response({})

    def put(self, request: Request) -> Response:
        return Response(request.data)
