import datetime

from gatherer.models import *
from tbot.models import *


class NotCategorizedDigestRecordsMixin:

    def not_categorized_records_queryset(self, from_bot: bool, project_name: str = 'FOSS News'):
        dt_now = datetime.datetime.now()
        dt_now_minus_1m = dt_now - datetime.timedelta(days=30)
        recent_foss_news_records = DigestRecord.objects.filter(projects__in=(Project.objects.filter(name=project_name)), gather_dt__gt=dt_now_minus_1m)
        unknown_state_queryset = recent_foss_news_records.filter(state='UNKNOWN')
        unknown_content_type_queryset = recent_foss_news_records.filter(content_type='UNKNOWN')
        none_content_type_queryset = recent_foss_news_records.filter(content_type=None)
        none_is_main_queryset = recent_foss_news_records.filter(is_main=None)
        none_content_category_queryset = recent_foss_news_records.filter(content_category=None).exclude(content_type='OTHER')
        partially_categorized_queryset = unknown_state_queryset | unknown_content_type_queryset | none_content_type_queryset | none_is_main_queryset | none_content_category_queryset
        if from_bot:
            recent_tbot_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(dt__gt=dt_now_minus_1m)
            recent_tbot_attempts_records_ids = [attempt.digest_record.id for attempt in recent_tbot_attempts]
            recent_foss_news_records = partially_categorized_queryset.filter(id__in=recent_tbot_attempts_records_ids)
            fully_categorized_records = recent_foss_news_records.filter(state='IN_DIGEST',
                                                                        content_type__in=DigestRecordContentType,
                                                                        content_category__in=DigestRecordContentCategory)
            recent_not_fully_categorized_foss_news_records = fully_categorized_records.exclude(pk__in=fully_categorized_records)
            return recent_not_fully_categorized_foss_news_records
        else:
            return partially_categorized_queryset.filter(digest_issue__number=DigestIssue.objects.order_by('-number')[0].number, state='IN_DIGEST')
