# Generated by Django 2.2.13 on 2021-08-21 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0036_fill_digest_records_sources'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='digestrecordssource',
            options={'verbose_name': 'Digest Records Source', 'verbose_name_plural': 'Digest Records Sources'},
        ),
    ]
