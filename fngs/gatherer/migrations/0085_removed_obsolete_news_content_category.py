# Generated by Django 2.2.24 on 2021-11-07 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0084_additional_renaming_after_recent_model_name_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='digestrecord',
            name='content_category',
            field=models.CharField(blank=True, choices=[('EVENTS', 'events'), ('INTROS', 'intros'), ('OPENING', 'opening'), ('ORG', 'org'), ('DIY', 'diy'), ('LAW', 'law'), ('KnD', 'knd'), ('SYSTEM', 'system'), ('SPECIAL', 'special'), ('EDUCATION', 'education'), ('DATABASES', 'db'), ('MULTIMEDIA', 'multimedia'), ('MOBILE', 'mobile'), ('SECURITY', 'security'), ('SYSADM', 'sysadm'), ('DEVOPS', 'devops'), ('DATA_SCIENCE', 'data_science'), ('WEB', 'web'), ('DEV', 'dev'), ('TESTING', 'testing'), ('HISTORY', 'history'), ('MANAGEMENT', 'management'), ('USER', 'user'), ('GAMES', 'games'), ('HARDWARE', 'hardware'), ('MESSENGERS', 'messengers'), ('MISC', 'misc')], max_length=15, null=True, verbose_name='Content Category'),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='content_category',
            field=models.CharField(blank=True, choices=[('EVENTS', 'events'), ('INTROS', 'intros'), ('OPENING', 'opening'), ('ORG', 'org'), ('DIY', 'diy'), ('LAW', 'law'), ('KnD', 'knd'), ('SYSTEM', 'system'), ('SPECIAL', 'special'), ('EDUCATION', 'education'), ('DATABASES', 'db'), ('MULTIMEDIA', 'multimedia'), ('MOBILE', 'mobile'), ('SECURITY', 'security'), ('SYSADM', 'sysadm'), ('DEVOPS', 'devops'), ('DATA_SCIENCE', 'data_science'), ('WEB', 'web'), ('DEV', 'dev'), ('TESTING', 'testing'), ('HISTORY', 'history'), ('MANAGEMENT', 'management'), ('USER', 'user'), ('GAMES', 'games'), ('HARDWARE', 'hardware'), ('MESSENGERS', 'messengers'), ('MISC', 'misc')], max_length=15, null=True, verbose_name='Content Category'),
        ),
    ]
