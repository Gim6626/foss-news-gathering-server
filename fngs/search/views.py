from django.shortcuts import render

from django.views.generic import TemplateView, ListView
from django.db.models import Q

from gatherer.models import DigestRecord


class SearchView(TemplateView):
    template_name = 'search.html'


class SearchResultsView(ListView):
    model = DigestRecord
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = DigestRecord.objects.filter(
            Q(title__icontains=query) | Q(url__icontains=query)
        )
        return object_list
