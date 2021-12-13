from rest_framework import routers
from tbot.views import *

router = routers.DefaultRouter()
router.register('user/simple',
                # OLD: 'telegram-bot-user'
                TelegramBotUserViewSet,
                basename='user')
router.register('user/detailed',
                # OLD: 'telegram-bot-user-detailed'
                TelegramBotUserDetailedViewSet,
                basename='user/detailed')
router.register('group',
                # OLD: 'telegram-bot-user-group'
                TelegramBotUserGroupViewSet,
                basename='group')
router.register('digest-record/categorization-attempt',
                # OLD: 'telegram-bot-digest-record-categorization-attempt'
                TelegramBotDigestRecordCategorizationAttemptViewSet,
                basename='digest-record/categorization-attempt')
router.register('digest-record/categorization-attempt/detailed',
                # OLD: 'telegram-bot-digest-record-categorization-attempt-detailed'
                TelegramBotDigestRecordCategorizationAttemptDetailedViewSet,
                basename='digest-record/categorization-attempt/detailed')
router.register('digest-record/not-categorized/random',
                # OLD: 'telegram-bot-one-random-not-categorized-foss-news-digest-record'
                TelegramBotOneRandomNotCategorizedDigestRecordViewSet,
                basename='digest-record/not-categorized/random')
router.register('digest-record/not-categorized/count',
                # OLD: 'telegram-bot-not-categorized-foss-news-digest-records-count'
                TelegramBotNotCategorizedDigestRecordsCountViewSet,
                basename='digest-record/not-categorized/count')
router.register('digest-record/categorized',
                # OLD: 'digest-records-categorized-by-tbot'
                DigestRecordsCategorizedByTbotViewSet,
                basename='digest-record/categorized')

urlpatterns = router.urls
