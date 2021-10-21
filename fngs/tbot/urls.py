from rest_framework import routers
from tbot.views import *

router = routers.DefaultRouter()
router.register('telegram-bot-user',
                TelegramBotUserViewSet,
                basename='telegram_bot_user')
router.register('telegram-bot-user-detailed',
                TelegramBotUserDetailedViewSet,
                basename='telegram_bot_user_detailed')
router.register('telegram-bot-user-group',
                TelegramBotUserGroupViewSet,
                basename='telegram_bot_user_group')
router.register('telegram-bot-digest-record-categorization-attempt',
                TelegramBotDigestRecordCategorizationAttemptViewSet,
                basename='telegram_bot_digest_record_categorization_attempt')
router.register('telegram-bot-digest-record-categorization-attempt-detailed',
                TelegramBotDigestRecordCategorizationAttemptDetailedViewSet,
                basename='telegram_bot_digest_record_categorization_attempt_detailed')
router.register('telegram-bot-one-random-not-categorized-foss-news-digest-record',
                TelegramBotOneRandomNotCategorizedFossNewsDigestRecordViewSet,
                basename='telegram_bot_one_random_not_categorized_foss_news_digest_record')
router.register('telegram-bot-not-categorized-foss-news-digest-records-count',
                TelegramBotNotCategorizedFossNewsDigestRecordsCountViewSet,
                basename='telegram_bot_not_categorized_foss_news_digest_records_count')
router.register('telegram-bot-user-by-tid',
                TelegramBotUserByTidViewSet,
                basename='telegram_bot_user_by_tid')
router.register('digest-records-categorized-by-tbot',
                DigestRecordsCategorizedByTbotViewSet,
                basename='digest_records_categorized_by_tbot')

urlpatterns = router.urls
