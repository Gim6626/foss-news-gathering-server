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
        filtered_objects = DigestRecord.objects.filter(
            Q(title__icontains=query) | Q(url__icontains=query)
        )
        ordered_filtered_objects = filtered_objects.order_by('-dt')
        return ordered_filtered_objects

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context
