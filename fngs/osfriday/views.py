from django.views.generic import ListView
from gatherer.models import (
    DigestRecord,
    Project,
)


class OsFridayFeedView(ListView):
    model = DigestRecord
    template_name = 'os_friday_rss.xml'

    def get_queryset(self):
        objects = DigestRecord.objects.filter(projects__in=Project.objects.filter(name='OS Friday')).order_by('-dt')[:1000]
        return objects
