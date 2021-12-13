import datetime

from gatherer.models import *
from tbot.models import *


class NotCategorizedDigestRecordsMixin:

    def not_categorized_records_queryset(self, from_bot: bool, project_name: str = 'FOSS News'):
        queryset = DigestRecord.objects.filter(projects__in=(Project.objects.filter(name=project_name)))
        unknown_state_queryset = queryset.filter(state='UNKNOWN')
        if from_bot:
            dt_now = datetime.datetime.now()
            dt_now_minus_2w = dt_now - datetime.timedelta(days=14)
            recent_tbot_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(dt__gt=dt_now_minus_2w)
            recent_tbot_attempts_records_ids = [attempt.digest_record.id for attempt in recent_tbot_attempts]
            queryset = unknown_state_queryset.filter(id__in=recent_tbot_attempts_records_ids)
            return queryset
        else:
            foss_news_current_queryset = queryset.filter(digest_issue__number=DigestIssue.objects.order_by('-number')[0].number, state='IN_DIGEST')
            unknown_content_type_queryset = foss_news_current_queryset.filter(content_type='UNKNOWN')
            none_content_type_queryset = foss_news_current_queryset.filter(content_type=None)
            none_is_main_queryset = foss_news_current_queryset.filter(is_main=None)
            none_content_category_queryset = foss_news_current_queryset.filter(content_category=None).exclude(content_type='OTHER')
            return unknown_state_queryset | unknown_content_type_queryset | none_content_type_queryset | none_is_main_queryset | none_content_category_queryset