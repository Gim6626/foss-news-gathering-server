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


# TODO: Obsolete, remove with removal of api/v1
class CurrentSimilarDigestRecordsFilter(filters.FilterSet):
    digest_issue = filters.NumberFilter(method='digest_filter')
    digest_record = filters.NumberFilter(method='similar_records_filter')

    class Meta:
        model = SimilarDigestRecords
        fields = [
            'digest_issue',
        ]

    def digest_filter(self, queryset, name, value):
        return queryset.filter(digest_issue=value)


class SimilarDigestRecordsFilter(filters.FilterSet):
    digest_issue = filters.NumberFilter(method='digest_issue_filter')
    digest_record = filters.NumberFilter(method='digest_record_filter')

    class Meta:
        model = SimilarDigestRecords
        fields = [
            'digest_issue',
            'digest_record',
        ]

    def digest_issue_filter(self, queryset, name, value):
        return queryset.filter(digest_issue=value)

    def digest_record_filter(self, queryset, name, value):
        return queryset.filter(digest_records__in=DigestRecord.objects.filter(pk=value))


class DigestRecordsLookingSimilarFilter(filters.FilterSet):
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


# TODO: Obsolete, remove with removal of api/v1
class SimilarDigestRecordsByDigestRecordFilter(filters.FilterSet):
    digest_record = filters.NumberFilter(method='similar_records_filter')

    class Meta:
        model = SimilarDigestRecords
        fields = [
            'digest_record',
        ]

    def similar_records_filter(self, queryset, name, value):
        return queryset.filter(digest_records__in=DigestRecord.objects.filter(pk=value))
