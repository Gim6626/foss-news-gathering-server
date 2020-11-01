from rest_framework import routers
import gatherer.views

router = routers.DefaultRouter()
router.register('digest-records', gatherer.views.DigestRecordViewSet, base_name='digest_records')

urlpatterns = router.urls
