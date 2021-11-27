from gatherer.models import *


class NotCategorizedDigestRecordsMixin:

    def not_categorized_records_queryset(self):
        foss_news_queryset = DigestRecord.objects.filter(projects__in=(Project.objects.filter(name='FOSS News')))
        unknown_state_queryset = foss_news_queryset.filter(state='UNKNOWN')
        foss_news_current_queryset = foss_news_queryset.filter(digest_issue__number=DigestIssue.objects.order_by('-number')[0].number, state='IN_DIGEST')
        unknown_content_type_queryset = foss_news_current_queryset.filter(content_type='UNKNOWN')
        none_content_type_queryset = foss_news_current_queryset.filter(content_type=None)
        none_is_main_queryset = foss_news_current_queryset.filter(is_main=None)
        none_content_category_queryset = foss_news_current_queryset.filter(content_category=None).exclude(content_type='OTHER')
        return unknown_state_queryset | unknown_content_type_queryset | none_content_type_queryset | none_is_main_queryset | none_content_category_queryset