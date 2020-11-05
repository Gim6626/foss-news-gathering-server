# Generated by Django 2.2.3 on 2020-11-05 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0001_create_digest_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='digestrecord',
            name='category',
            field=models.CharField(blank=True, choices=[('UNKNOWN', 'unknown'), ('NEWS', 'news'), ('ARTICLES', 'articles'), ('RELEASES', 'releases'), ('OTHER', 'other')], max_length=256, null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='digestrecord',
            name='digest_number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Digest Number'),
        ),
        migrations.AddField(
            model_name='digestrecord',
            name='is_main',
            field=models.BooleanField(blank=True, null=True, verbose_name='Is main post'),
        ),
        migrations.AddField(
            model_name='digestrecord',
            name='subcategory',
            field=models.CharField(blank=True, choices=[('EVENTS', 'events'), ('INTROS', 'intros'), ('OPENING', 'opening'), ('NEWS', 'news'), ('DIY', 'diy'), ('LAW', 'law'), ('KnD', 'knd'), ('SYSTEM', 'system'), ('SPECIAL', 'special'), ('MULTIMEDIA', 'multimedia'), ('SECURITY', 'security'), ('DEVOPS', 'devops'), ('DATA_SCIENCE', 'data_science'), ('WEB', 'web'), ('DEV', 'dev'), ('MANAGEMENT', 'management'), ('USER', 'user'), ('GAMES', 'games'), ('HARDWARE', 'hardware'), ('MISC', 'misc')], max_length=256, null=True, verbose_name='Subcategory'),
        ),
    ]
