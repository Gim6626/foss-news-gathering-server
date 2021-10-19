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
    content_type = filters.CharFilter(method='content_type_filter')
    content_category = filters.CharFilter(method='content_category_filter')

    class Meta:
        model = DigestRecord
        fields = [
            'digest_issue',
            'content_type',
            'content_category'
        ]

    def digest_filter(self, queryset, name, value):
        return queryset.filter(digest_issue=value)

    def content_type_filter(self, queryset, name, value):
        return queryset.filter(content_type=value)

    def content_category_filter(self, queryset, name, value):
        return queryset.filter(content_category=value)


class DuplicatesByDigestRecordFilter(filters.FilterSet):
    digest_record = filters.NumberFilter(method='duplicates_filter')

    class Meta:
        model = DigestRecordDuplicate
        fields = [
            'digest_record',
        ]

    def duplicates_filter(self, queryset, name, value):
        return queryset.filter(digest_records__in=DigestRecord.objects.filter(pk=value))
