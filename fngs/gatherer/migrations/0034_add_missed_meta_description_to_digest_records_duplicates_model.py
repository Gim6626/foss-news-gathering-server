# Generated by Django 2.2.13 on 2021-08-21 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0033_add_digestrecord_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='digestrecordduplicate',
            options={'verbose_name': 'Digest Record Duplicate', 'verbose_name_plural': 'Digest Records Duplicates'},
        ),
    ]
