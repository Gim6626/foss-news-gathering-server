# Generated by Django 2.2.13 on 2021-08-21 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0034_add_missed_meta_description_to_digest_records_duplicates_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigestRecordsSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('enabled', models.BooleanField(verbose_name='Enabled')),
            ],
        ),
    ]
