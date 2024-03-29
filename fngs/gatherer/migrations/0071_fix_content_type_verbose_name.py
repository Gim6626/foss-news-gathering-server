# Generated by Django 2.2.24 on 2021-10-19 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0070_rename_category_to_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='digestrecord',
            name='content_type',
            field=models.CharField(blank=True, choices=[('UNKNOWN', 'unknown'), ('NEWS', 'news'), ('ARTICLES', 'articles'), ('VIDEOS', 'videos'), ('RELEASES', 'releases'), ('OTHER', 'other')], max_length=15, null=True, verbose_name='Content Type'),
        ),
    ]
