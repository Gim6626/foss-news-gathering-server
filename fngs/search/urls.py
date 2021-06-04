from django.urls import path

from .views import SearchView, SearchResultsView

urlpatterns = [
    path('search-results/', SearchResultsView.as_view(), name='search_results'),
    path('search/', SearchView.as_view(), name='home'),
]
