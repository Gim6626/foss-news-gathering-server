from django.db import migrations

from bs4 import BeautifulSoup

from gatherer.models import (
    DigestRecord
)


def fill_cleared_descriptions(apps, schema_editor):
    digest_records_with_not_empty_descriptions = DigestRecord.objects.exclude(description=None)
    for dr in digest_records_with_not_empty_descriptions:
        dr.cleared_description = BeautifulSoup(dr.description, 'lxml').text
        dr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0078_digestrecord_cleared_description'),
    ]

    operations = [
        migrations.RunPython(fill_cleared_descriptions, migrations.RunPython.noop),
    ]
