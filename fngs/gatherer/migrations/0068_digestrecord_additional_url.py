# Generated by Django 2.2.24 on 2021-10-01 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0067_added_skipped_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='digestrecord',
            name='additional_url',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Additional URL'),
        ),
    ]
