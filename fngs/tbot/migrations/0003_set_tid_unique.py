# Generated by Django 2.2.13 on 2021-08-21 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tbot', '0002_set_telegram_username_not_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrambotuser',
            name='tid',
            field=models.IntegerField(unique=True, verbose_name='Telegram User ID'),
        ),
    ]
