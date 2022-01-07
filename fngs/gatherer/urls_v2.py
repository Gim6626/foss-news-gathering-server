from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from gatherer.views import *

router = routers.DefaultRouter()
router.register('digest-record',
                # OLD: 'digest-records',
                DigestRecordViewSet,
                basename='digest-record')
router.register('digest-record/not-categorized',
                # OLD: 'new-digest-records'
                NewFossNewsDigestRecordViewSet,
                basename='digest-record/not-categorized')
router.register('digest-record/not-categorized/oldest',
                # OLD: 'one-new-foss-news-digest-record'
                OldestNotCategorizedDigestRecordViewSet,
                basename='digest-record/not-categorized/oldest')
router.register('digest-record/not-categorized/count',
                # OLD: 'not-categorized-digest-records-count'
                NotCategorizedDigestRecordsCountViewSet,
                basename='digest-record/not-categorized/count')
router.register('similar-digest-record',
                # OLD: 'similar-digest-records',
                SimilarDigestRecordsViewSet,
                basename='similar-digest-record')
router.register('project',
                # OLD: 'projects'
                ProjectViewSet,
                basename='project')
router.register('keyword',
                # OLD: 'keywords'
                KeywordViewSet,
                basename='keyword')
router.register('digest-issue',
                # OLD: 'digest-issues'
                DigestIssueViewSet,
                basename='digest-issue')
router.register('content-category/guess',
                # OLD: 'guess-content-category'
                GuessContentCategoryView,
                basename='content-category/guess')
router.register('digest-issue/(?P<digest_number>.*?)/previous/similar-records',
                SimilarRecordsInPreviousNonSpecialDigest,
                basename='similar-records-in-previous-digest')

urlpatterns = router.urls
