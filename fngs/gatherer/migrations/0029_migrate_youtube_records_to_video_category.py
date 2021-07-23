# Generated by Django 2.2.13 on 2021-07-14 04:03

from django.db import migrations, models
from gatherer.models import DigestRecord, DigestRecordCategory


def migrate_youtube_records_to_video_category(apps, schema_editor):
    dr_model = apps.get_model('gatherer', 'DigestRecord')
    dr: DigestRecord
    for dr in dr_model.objects.all():
        if 'https://www.youtube.com' in dr.url and dr.category:
            dr.category = DigestRecordCategory.VIDEOS.name
            dr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0028_add_video_category'),
    ]

    operations = [
        migrations.RunPython(migrate_youtube_records_to_video_category, migrations.RunPython.noop),
    ]