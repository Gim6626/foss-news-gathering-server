# Generated by Django 2.2.24 on 2021-10-19 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0074_rename_keyword_category_to_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='content_category',
            field=models.CharField(blank=True, choices=[('EVENTS', 'events'), ('INTROS', 'intros'), ('OPENING', 'opening'), ('NEWS', 'news'), ('ORG', 'org'), ('DIY', 'diy'), ('LAW', 'law'), ('KnD', 'knd'), ('SYSTEM', 'system'), ('SPECIAL', 'special'), ('EDUCATION', 'education'), ('DATABASES', 'db'), ('MULTIMEDIA', 'multimedia'), ('MOBILE', 'mobile'), ('SECURITY', 'security'), ('SYSADM', 'sysadm'), ('DEVOPS', 'devops'), ('DATA_SCIENCE', 'data_science'), ('WEB', 'web'), ('DEV', 'dev'), ('TESTING', 'testing'), ('HISTORY', 'history'), ('MANAGEMENT', 'management'), ('USER', 'user'), ('GAMES', 'games'), ('HARDWARE', 'hardware'), ('MESSENGERS', 'messengers'), ('MISC', 'misc')], max_length=15, null=True, verbose_name='Content Category'),
        ),
    ]