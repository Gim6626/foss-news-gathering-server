from django.db import migrations, models
from gatherer.models import (
    Keyword
)


def disable_some_keywords(apps, schema_editor):
    for keyword in Keyword.objects.all():
        if keyword.name.lower() in ('links', 'go', 'make', 'launch', 'watch'):
            keyword.enabled = False
            keyword.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0065_keyword_enabled'),
    ]

    operations = [
        migrations.RunPython(disable_some_keywords, migrations.RunPython.noop),
    ]
