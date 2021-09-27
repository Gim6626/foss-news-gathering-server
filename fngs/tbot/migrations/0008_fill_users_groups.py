from django.db import migrations, models
from tbot.models import (
    TelegramBotUser,
    TelegramBotUserGroup,
)


def fill_users_groups(apps, schema_editor):
    users_users_group = TelegramBotUserGroup(name='users')
    users_users_group.save()
    admins_users_group = TelegramBotUserGroup(name='admins')
    admins_users_group.save()
    for user in TelegramBotUser.objects.all():
        groups = [users_users_group]
        if user.username == 'gim6626':
            groups.append(admins_users_group)
        user.groups.set(groups)
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tbot', '0007_telegrambotusergroup'),
    ]

    operations = [
        migrations.RunPython(fill_users_groups, migrations.RunPython.noop),
    ]
