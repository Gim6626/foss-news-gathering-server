from django.urls import path
from rest_framework import routers
from gatherer.views import *
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

router = routers.DefaultRouter()
router.register('digest-record',
                # OLD: 'digest-records',
                DigestRecordViewSet)
router.register('digest-record/not-categorized',
                # OLD: 'new-digest-records'
                NewFossNewsDigestRecordViewSet)
router.register('digest-record/not-categorized/oldest',
                # OLD: 'one-new-foss-news-digest-record'
                OldestNotCategorizedDigestRecordViewSet)
router.register('digest-record/not-categorized/count',
                # OLD: 'not-categorized-digest-records-count'
                NotCategorizedDigestRecordsCountViewSet)
router.register('digest-record/detailed',
                # OLD: 'specific-digest-records',
                DetailedDigestRecordViewSet)
router.register('similar-digest-record',
                # OLD: 'similar-digest-records',
                SimilarDigestRecordsViewSet)
router.register('similar-digest-record/detailed',
                # OLD: 'similar-digest-records-detailed',
                SimilarDigestRecordsDetailedViewSet)
router.register('digest-record/similar',
                # OLD: 'digest-records-looking-similar',
                DigestRecordsLookingSimilarViewSet)
router.register('project',
                # OLD: 'projects'
                ProjectViewSet)
router.register('keyword',
                # OLD: 'keywords'
                KeywordViewSet)
router.register('digest-issue',
                # OLD: 'digest-issues'
                DigestIssueViewSet)
router.register('content-category/guess',
                # OLD: 'guess-content-category'
                GuessContentCategoryView)
# TODO: Rewrite ViewSet in style similar to other new endpoints
router.register('similar-records-in-previous-digest',
                SimilarRecordsInPreviousDigest)

urlpatterns += router.urls
