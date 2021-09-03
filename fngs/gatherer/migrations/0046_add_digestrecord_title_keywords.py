# Generated by Django 2.2.13 on 2021-08-22 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0045_connect_digest_records_to_issues'),
    ]

    operations = [
        migrations.AddField(
            model_name='digestrecord',
            name='title_keywords',
            field=models.ManyToManyField(blank=True, related_name='records', to='gatherer.Keyword', verbose_name='Title Keywords'),
        ),
    ]