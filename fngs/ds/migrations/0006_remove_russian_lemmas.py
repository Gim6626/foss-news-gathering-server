from django.db import migrations

from gatherer.models import *
from ds.models import *


def remove_russian_lemmas(apps, schema_editor):
    russian_records = DigestRecord.objects.filter(language=Language.RUSSIAN.name)
    russian_records_lemmas = DigestRecordLemma.objects.filter(digest_record__in=russian_records)
    drl: DigestRecordLemma
    removed_connections_count = 0
    removed_lemmas_count = 0
    lemmas_to_remove = []
    for drl in russian_records_lemmas:
        remove_only_connection = False
        if DigestRecordLemma.objects.filter(lemma=drl.lemma, digest_record__in=DigestRecord.objects.filter(language=Language.ENGLISH.name)):
            remove_only_connection = True
        lemma = drl.lemma
        drl.delete()
        removed_connections_count += 1
        if not remove_only_connection:
            lemmas_to_remove.append(lemma)
    for lemma in lemmas_to_remove:
        lemma.delete()
        removed_lemmas_count += 1
    print(f'Removed {removed_connections_count} connections')
    print(f'Removed {removed_lemmas_count} lemmas')


class Migration(migrations.Migration):

    dependencies = [
        ('ds', '0005_fill_lemmas_and_connections_to_digest_records'),
    ]

    operations = [
        migrations.RunPython(remove_russian_lemmas, migrations.RunPython.noop),
    ]
