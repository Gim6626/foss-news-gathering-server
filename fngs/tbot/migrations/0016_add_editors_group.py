from django.db import migrations
from tbot.models import (
    TelegramBotUserGroup,
)


def add_editors_group(apps, schema_editor):
    editors_group = TelegramBotUserGroup(name='editors')
    editors_group.save()


def delete_editors_group(apps, schema_editor):
    TelegramBotUserGroup.objects.filter(name='editors').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tbot', '0015_fix_estimated_content_category_verbose_name'),
    ]

    operations = [
        migrations.RunPython(add_editors_group, delete_editors_group),
    ]
