# Generated by Django 2.2.13 on 2021-08-21 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tbot', '0001_add_user_and_categorization_attempt_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrambotuser',
            name='username',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Telegram Username'),
        ),
    ]
