from django.db import migrations

from gatherer.models import (
    Keyword,
    DigestRecord,
)


def remove_jenkins_duplicate(apps, schema_editor):
    queryset = Keyword.objects.filter(id=1652, name='Jenkins')
    if not queryset:
        print('"Bad" Jenkins keyword not found, nothing to do')
        return
    jbad = queryset[0]
    queryset = Keyword.objects.filter(id=535, name='Jenkins')
    if not queryset:
        print('"Good" Jenkins keyword not found, nothing to do')
        return
    jgood = queryset[0]
    digest_record_object: DigestRecord
    fixed_count = 0
    for digest_record_object in DigestRecord.objects.filter(title_keywords__in=(jbad,)):
        keywords_new = [k for k in digest_record_object.title_keywords.all() if k != jbad]
        if jgood not in keywords_new:
            keywords_new.append(jgood)
        digest_record_object.title_keywords.set(keywords_new)
        digest_record_object.save()
        print(f'Fixed digest record #{digest_record_object.id} "{digest_record_object.title}"')
        fixed_count += 1
    print(f'"Bad" Jenkins keywords removed from {fixed_count} digest records')
    jbad.delete()
    print('"Bad" Jenkins keyword removed from DB')


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0081_fix_wrongly_skipped_records'),
    ]

    operations = [
        migrations.RunPython(remove_jenkins_duplicate, migrations.RunPython.noop),
    ]
