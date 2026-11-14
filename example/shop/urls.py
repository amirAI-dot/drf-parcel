from django.urls import path
from rest_framework.routers import DefaultRouter

from shop import api

router = DefaultRouter()
router.register('products', api.ProductViewSet)
router.register('orders', api.OrderViewSet)

urlpatterns = [
    path('health/', api.HealthView.as_view()),
    *router.urls,
]
