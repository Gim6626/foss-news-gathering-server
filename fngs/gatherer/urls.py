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
router.register('specific-digest-records', SpecificDigestRecordsViewSet, basename='specific_digest_records')
router.register('digest-records-duplicates', DigestRecordDuplicateViewSet, basename='digest_records_duplicates')
router.register('similar-digest-records-duplicates', SimilarDigestRecordsViewSet, basename='similar_digest_records')
router.register('duplicates-by-digest-record', DuplicatesByDigestRecordsViewSet, basename='duplicates_by_digest_record')

urlpatterns += router.urls
