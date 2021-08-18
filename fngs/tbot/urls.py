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
router.register('telegram-bot-not-categorized-foss-news-digest-records',
                TelegramBotNotCategorizedFossNewsDigestRecordsViewSet,
                base_name='telegram_bot_not_categorized_foss_news_digest_records')

urlpatterns = router.urls
