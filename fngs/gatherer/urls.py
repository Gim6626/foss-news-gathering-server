from django.urls import path
from rest_framework import routers
import gatherer.views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('specific-digest-records/<int:digest_id>/', gatherer.views.specific_digest_records, name='specific_digest_records'),
]

router = routers.DefaultRouter()
router.register('digest-records', gatherer.views.DigestRecordViewSet, base_name='digest_records')
router.register('new-digest-records', gatherer.views.NewDigestRecordViewSet, base_name='new_digest_records')

urlpatterns += router.urls
