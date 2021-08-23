from django_filters import rest_framework as filters
from gatherer.models import *


class SpecificDigestRecordsFilter(filters.FilterSet):
    digest_issue = filters.NumberFilter(method='digest_filter')

    class Meta:
        model = DigestRecord
        fields = [
            'digest_issue',
        ]

    def digest_filter(self, queryset, name, value):
        return queryset.filter(digest_issue=value)


class CurrentDigestRecordsDuplicatesFilter(filters.FilterSet):
    digest_issue = filters.NumberFilter(method='digest_filter')

    class Meta:
        model = DigestRecordDuplicate
        fields = [
            'digest_issue',
        ]

    def digest_filter(self, queryset, name, value):
        return queryset.filter(digest_issue=value)


class SimilarDigestRecordsFilter(filters.FilterSet):
    digest_issue = filters.NumberFilter(method='digest_filter')
    category = filters.CharFilter(method='category_filter')
    subcategory = filters.CharFilter(method='subcategory_filter')

    class Meta:
        model = DigestRecord
        fields = [
            'digest_issue',
            'category',
            'subcategory'
        ]

    def digest_filter(self, queryset, name, value):
        return queryset.filter(digest_issue=value)

    def category_filter(self, queryset, name, value):
        return queryset.filter(category=value)

    def subcategory_filter(self, queryset, name, value):
        return queryset.filter(subcategory=value)


class DuplicatesByDigestRecordFilter(filters.FilterSet):
    digest_record = filters.NumberFilter(method='duplicates_filter')

    class Meta:
        model = DigestRecordDuplicate
        fields = [
            'digest_record',
        ]

    def duplicates_filter(self, queryset, name, value):
        return queryset.filter(digest_records__in=DigestRecord.objects.filter(pk=value))
