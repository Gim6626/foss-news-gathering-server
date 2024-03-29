# Generated by Django 2.2.13 on 2021-09-12 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0054_digestgatheringiteration'),
    ]

    operations = [
        migrations.AddField(
            model_name='digestgatheringiteration',
            name='parser_error',
            field=models.TextField(blank=True, null=True, verbose_name='Parser error'),
        ),
        migrations.AddField(
            model_name='digestgatheringiteration',
            name='source_enabled',
            field=models.BooleanField(blank=True, null=True, verbose_name='Source enabled'),
        ),
        migrations.AddField(
            model_name='digestgatheringiteration',
            name='source_error',
            field=models.TextField(blank=True, null=True, verbose_name='Source error'),
        ),
    ]
