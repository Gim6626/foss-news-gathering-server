# Generated by Django 2.2.3 on 2020-11-05 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0002_digest_record_new_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='digestrecord',
            name='state',
            field=models.CharField(blank=True, choices=[('UNKNOWN', 'unknown'), ('IN_DIGEST', 'in_digest'), ('IGNORED', 'ignored')], max_length=256, null=True, verbose_name='State'),
        ),
    ]
