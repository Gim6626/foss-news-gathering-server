from django.urls import path

from .views import OsFridayFeedView

urlpatterns = [
    path('os-friday/feed', OsFridayFeedView.as_view(), name='os_friday_feed'),
]
