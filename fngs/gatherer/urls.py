from rest_framework import routers
from gatherer.views import *

urlpatterns = []

router = routers.DefaultRouter()
router.register('digest-records', DigestRecordViewSet, basename='digest_records')
router.register('new-digest-records', NewDigestRecordViewSet, basename='new_digest_records')
router.register('new-foss-news-digest-records', NewFossNewsDigestRecordViewSet, basename='new_foss_news_digest_records')
router.register('one-new-foss-news-digest-record', OneNewFossNewsDigestRecordViewSet, basename='one_new_foss_news_digest_record')
router.register('one-new-foss-news-digest-record-from-tbot', OneNewFossNewsDigestRecordFromTbotViewSet, basename='one_new_foss_news_digest_record_from_tbot')
router.register('not-categorized-digest-records-count', NotCategorizedDigestRecordsCountViewSet, basename='not_categorized_digest_records_count')
router.register('not-categorized-digest-records-from-tbot-count', NotCategorizedDigestRecordsFromTbotCountViewSet, basename='not_categorized_digest_records_from_tbot_count')
router.register('specific-digest-records', SpecificDigestRecordsViewSet, basename='specific_digest_records')
router.register('similar-digest-records', SimilarDigestRecordsViewSet, basename='similar_digest_records')
router.register('similar-digest-records-detailed', SimilarDigestRecordsDetailedViewSet, basename='digessimilar_digest_records_detailed')
router.register('digest-records-looking-similar', DigestRecordsLookingSimilarViewSet, basename='similar_digest_records_by_fields')
router.register('similar-digest-records-by-digest-record', SimilarDigestRecordsByDigestRecordViewSet, basename='similar_digest_records_by_digest_record')
router.register('projects', ProjectViewSet, basename='projects')
router.register('keywords', KeywordViewSet, basename='keywords')
router.register('digest-issues', DigestIssueViewSet, basename='digest_issues')
router.register('guess-content-category', GuessContentCategoryView, basename='guess_category')
router.register('similar-records-in-previous-digest', SimilarRecordsInPreviousDigest, basename='similar_records_in_previous_digest')

urlpatterns += router.urls
