# Generated by Django 2.2.24 on 2021-11-07 01:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0085_removed_obsolete_news_content_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='digestrecord',
            name='digest_number',
        ),
        migrations.RemoveField(
            model_name='similardigestrecords',
            name='digest_number',
        ),
    ]
