from django.urls import path
from rest_framework import routers
from gatherer.views import *
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

router = routers.DefaultRouter()
router.register('digest-records', DigestRecordViewSet, base_name='digest_records')
router.register('new-digest-records', NewDigestRecordViewSet, base_name='new_digest_records')
router.register('new-foss-news-digest-records', NewFossNewsDigestRecordViewSet, base_name='new_foss_news_digest_records')
router.register('specific-digest-records', SpecificDigestRecordsViewSet, basename='specific_digest_records')
router.register('digest-records-duplicates', DigestRecordDuplicateViewSet, basename='digest_records_duplicates')
router.register('digest-records-duplicates-detailed', DigestRecordDuplicateDetailedViewSet, basename='digest_records_duplicates_detailed')
router.register('similar-digest-records', SimilarDigestRecordsViewSet, basename='similar_digest_records')
router.register('duplicates-by-digest-record', DuplicatesByDigestRecordsViewSet, basename='duplicates_by_digest_record')
router.register('projects', ProjectViewSet, basename='projects')
router.register('keywords', KeywordViewSet, basename='keywords')
router.register('guess-category', GuessCategoryView, basename='guess_category')

urlpatterns += router.urls
