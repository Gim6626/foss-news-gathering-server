# Generated by Django 2.2.13 on 2021-09-12 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0055_add_more_fields_to_digestgatheringiteration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='digestgatheringiteration',
            old_name='count',
            new_name='gathered_count',
        ),
    ]
