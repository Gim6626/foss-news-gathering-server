from rest_framework import routers
from tbot.views import *

router = routers.DefaultRouter()
router.register('user',
                # OLD: 'telegram-bot-user'
                TelegramBotUserViewSet)
router.register('user/detailed',
                # OLD: 'telegram-bot-user-detailed'
                TelegramBotUserDetailedViewSet)
router.register('group',
                # OLD: 'telegram-bot-user-group'
                TelegramBotUserGroupViewSet)
router.register('digest-record/categorization-attempt',
                # OLD: 'telegram-bot-digest-record-categorization-attempt'
                TelegramBotDigestRecordCategorizationAttemptViewSet)
router.register('digest-record/categorization-attempt/detailed',
                # OLD: 'telegram-bot-digest-record-categorization-attempt-detailed'
                TelegramBotDigestRecordCategorizationAttemptDetailedViewSet)
router.register('digest-record/not-categorized/random',
                # OLD: 'telegram-bot-one-random-not-categorized-foss-news-digest-record'
                TelegramBotOneRandomNotCategorizedDigestRecordViewSet)
router.register('digest-record/not-categorized/count',
                # OLD: 'telegram-bot-not-categorized-foss-news-digest-records-count'
                TelegramBotNotCategorizedDigestRecordsCountViewSet)
router.register('digest-record/categorized',
                # OLD: 'digest-records-categorized-by-tbot'
                DigestRecordsCategorizedByTbotViewSet)

urlpatterns = router.urls
