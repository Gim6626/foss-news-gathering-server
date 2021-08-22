# Generated by Django 2.2.13 on 2021-07-14 04:03
import logging
import os
import json

from django.db import migrations, models
from gatherer.models import Keyword, DigestRecord


def fill_title_keywords(apps, schema_editor):
    for digest_record in DigestRecord.objects.all():
        if not digest_record.keywords:
            continue
        keywords = digest_record.keywords.split(';')
        keywords_to_store = []
        for keyword in keywords:
            keywords_from_db = Keyword.objects.filter(name__iexact=keyword)
            keywords_from_db_len = len(keywords_from_db)
            if keywords_from_db_len == 0:
                logging.error(f'Failed to find keyword "{keyword}" from digest record #{digest_record.id}')
                continue
            elif keywords_from_db_len > 1:
                logging.error(f'There are more than 1 keyword with name "{keyword}" in database (searched for digest record #{digest_record.id})')
                continue
            keywords_to_store.append(keywords_from_db[0])
        digest_record.title_keywords.set(keywords_to_store)
        digest_record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0046_add_digestrecord_title_keywords'),
    ]

    operations = [
        migrations.RunPython(fill_title_keywords, migrations.RunPython.noop),
    ]
