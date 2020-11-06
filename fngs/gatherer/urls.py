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

urlpatterns += router.urls
