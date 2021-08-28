from django.db import migrations
from gatherer.models import (
    DigestRecordsSource,
)

OSM_SOURCE_NAME = 'WeeklyOsm'


def add_osm_source(apps, schema_editor):
    osm_source = DigestRecordsSource(name=OSM_SOURCE_NAME, enabled=True)
    osm_source.save()


def remove_osm_source(apps, schema_editor):
    osm_source = DigestRecordsSource.objects.get(name=OSM_SOURCE_NAME)
    osm_source.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0052_fill_digest_issues_in_duplicates'),
    ]

    operations = [
        migrations.RunPython(add_osm_source, remove_osm_source),
    ]
