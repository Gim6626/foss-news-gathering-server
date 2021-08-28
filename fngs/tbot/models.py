from django.db import models

from gatherer.models import *


class TelegramBotUser(models.Model):

    tid = models.IntegerField(verbose_name='Telegram User ID',
                              unique=True)
    username = models.CharField(verbose_name='Telegram Username',
                                max_length=256,
                                blank=True,
                                null=True)

    class Meta:
        verbose_name = 'Telegram Bot User'
        verbose_name_plural = 'Telegram Bot Users'

    def __str__(self):
        return f'{self.username} (#{self.tid})'


class TelegramBotDigestRecordCategorizationAttempt(models.Model):

    dt = models.DateTimeField(verbose_name='Attempt Date&Time')
    telegram_bot_user = models.ForeignKey(to=TelegramBotUser,
                                          verbose_name='Telegram Bot User',
                                          on_delete=models.PROTECT)
    digest_record = models.ForeignKey(to=DigestRecord,
                                      related_name='tbot_estimations',
                                      verbose_name='Digest Record under Categorization',
                                      on_delete=models.PROTECT)
    estimated_state = models.CharField(verbose_name='Estimated State',
                                       choices=DigestRecordState.choices(),
                                       max_length=15,
                                       null=True,
                                       blank=True)
    estimated_is_main = models.BooleanField(verbose_name='Estimated Is Main Post',
                                            null=True,
                                            blank=True)
    estimated_category = models.CharField(verbose_name='Estimated Category',
                                          choices=DigestRecordCategory.choices(),
                                          max_length=15,
                                          null=True,
                                          blank=True)
    estimated_subcategory = models.CharField(verbose_name='Estimated Subcategory',
                                             choices=DigestRecordSubcategory.choices(),
                                             max_length=15,
                                             null=True,
                                             blank=True)

    class Meta:
        verbose_name = 'Telegram Bot Digest Record Categorization Attempt'
        verbose_name_plural = 'Telegram Bot Digest Record Categorization Attempts'
