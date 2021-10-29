from django.db import migrations

import datetime
import dateutil.parser

from gatherer.models import (
    DigestRecord,
    DigestRecordState,
)


def fix_wrongly_skipped_records(apps, schema_editor):
    recent_skipped_records = DigestRecord.objects.filter(state=DigestRecordState.SKIPPED.name, gather_dt__gt=datetime.datetime.now(tz=dateutil.tz.tzlocal()) - datetime.timedelta(days=7))
    fixed_count = 0
    for dr in recent_skipped_records:
        all_keywords_proprietary = True
        all_keywords_disabled = True
        for k in dr.title_keywords.all():
            if not k.proprietary:
                all_keywords_proprietary = False
            if k.enabled:
                all_keywords_disabled = False
        if not all_keywords_proprietary and not all_keywords_disabled:
            dr.state = DigestRecordState.UNKNOWN.name
            dr.save()
            fixed_count += 1
    print(f'Fixed {fixed_count} wrongly skipped records')


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0080_fixed_cleared_description_verbose_name'),
    ]

    operations = [
        migrations.RunPython(fix_wrongly_skipped_records, migrations.RunPython.noop),
    ]
