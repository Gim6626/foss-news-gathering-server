from django_filters import rest_framework as filters
from gatherer.models import *


class SpecificDigestRecordsFilter(filters.FilterSet):
    digest_number = filters.NumberFilter(method='digest_filter')

    class Meta:
        model = DigestRecord
        fields = [
            'digest_number',
        ]

    def digest_filter(self, queryset, name, value):
        return queryset.filter(digest_number=value)
