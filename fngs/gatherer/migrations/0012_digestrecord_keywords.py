# Generated by Django 2.2.13 on 2021-02-22 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0011_digestrecord_title_set_to_be_not_mandatory_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='digestrecord',
            name='keywords',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Keywords'),
        ),
    ]