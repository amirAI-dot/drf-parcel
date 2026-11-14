"""
The shop's own errors.

``OutOfStockError`` and ``StillOrderedError`` are the library's kind: a status, a code
the client branches on, a sentence, and ``data`` the client can act on.

``PaymentRequiredError`` is written the way a project wrote its errors before the
library - DRF's own ``APIException``, no ``data`` - and answers in the envelope
all the same, unchanged.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

from drf_parcel.exceptions import DomainError


# --8<-- [start:domain]
class OutOfStockError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'out_of_stock'
    default_detail = _('There is not enough of this product in stock.')


class StillOrderedError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'still_ordered'
    default_detail = _('This product has orders, and cannot be deleted.')


# --8<-- [end:domain]


# --8<-- [start:legacy]
class PaymentRequiredError(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_code = 'payment_required'
    default_detail = _('This order is not paid yet.')


# --8<-- [end:legacy]
