# Generated by Django 2.2.24 on 2021-10-24 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0079_fill_cleared_descriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='digestrecord',
            name='cleared_description',
            field=models.TextField(blank=True, null=True, verbose_name='Cleared description'),
        ),
    ]
