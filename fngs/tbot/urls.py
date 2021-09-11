from rest_framework import routers
from tbot.views import *

router = routers.DefaultRouter()
router.register('telegram-bot-user',
                TelegramBotUserViewSet,
                base_name='telegram_bot_user')
router.register('telegram-bot-digest-record-categorization-attempt',
                TelegramBotDigestRecordCategorizationAttemptViewSet,
                base_name='telegram_bot_digest_record_categorization_attempt')
router.register('telegram-bot-digest-record-categorization-attempt-detailed',
                TelegramBotDigestRecordCategorizationAttemptDetailedViewSet,
                base_name='telegram_bot_digest_record_categorization_attempt_detailed')
router.register('telegram-bot-one-random-not-categorized-foss-news-digest-record',
                TelegramBotOneRandomNotCategorizedFossNewsDigestRecordViewSet,
                base_name='telegram_bot_one_random_not_categorized_foss_news_digest_record')
router.register('telegram-bot-not-categorized-foss-news-digest-records-count',
                TelegramBotNotCategorizedFossNewsDigestRecordsCountViewSet,
                base_name='telegram_bot_not_categorized_foss_news_digest_records_count')
router.register('telegram-bot-user-by-tid',
                TelegramBotUserByTidViewSet,
                base_name='telegram_bot_user_by_tid')

urlpatterns = router.urls
