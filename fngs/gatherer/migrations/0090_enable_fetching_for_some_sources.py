from django.db import migrations

from gatherer.models import (
    DigestRecordsSource
)


sources_codes = (
    'OpenNetRu',
    'LosstRu',
    'HabrComGit',
    'HabrComSysAdm',
    'HabrComDevOps',
    'HabrComNix',
    'HabrComLinuxDev',
    'HabrComLinux',
    'HabrComOpenSource',
    'HabrComNews',
)


def enable_fetching_for_some_sources(apps, schema_editor):
    sources = DigestRecordsSource.objects.filter(name__in=sources_codes)
    s: DigestRecordsSource
    for s in sources:
        s.text_fetching_enabled = True
        s.save()


def disable_fetching_for_some_sources(apps, schema_editor):
    sources = DigestRecordsSource.objects.filter(name__in=sources_codes)
    s: DigestRecordsSource
    for s in sources:
        s.text_fetching_enabled = False
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0089_digestrecordssource_text_fetching_enabled'),
    ]

    operations = [
        migrations.RunPython(enable_fetching_for_some_sources, disable_fetching_for_some_sources),
    ]
