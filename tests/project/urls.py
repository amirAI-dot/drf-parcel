from django.urls import path
from rest_framework.routers import SimpleRouter

from tests.project import failures, views
from tests.project.shelf import views as shelf

router = SimpleRouter()
router.register('rings', views.RingViewSet, basename='ring')
router.register('named-rings', views.NamedRingViewSet, basename='named-ring')

urlpatterns = [
    path('totals/', views.TotalsView.as_view()),
    path('explained/', views.ExplainedView.as_view()),
    path('plain/', views.PlainView.as_view()),
    path('webhook/', views.OptedOutView.as_view()),
    path('not-json/', views.NotJsonView.as_view()),
    path('csv/', views.CsvView.as_view()),
    path('items/', shelf.ItemList.as_view()),
    path('items/sized/', shelf.SizedItemList.as_view()),
    path('items/unpaged/', shelf.UnpagedItemList.as_view()),
    path('items/four/', shelf.FourAPageItemList.as_view()),
    path('items/plain/', shelf.PlainItemList.as_view()),
    path('feed/', shelf.Feed.as_view()),
    path('feed/oldest-first/', shelf.OldestFirstFeed.as_view()),
    path('fail/<str:how>/', failures.FailingView.as_view()),
    path('orders/', failures.OrderView.as_view()),
    path('orders/many/', failures.ManyOrdersView.as_view()),
    path('signed-in/', failures.SignedInView.as_view()),
    path('tags/', failures.TagView.as_view()),
    path('read-only/', failures.ReadOnlyView.as_view()),
    *router.urls,
]
