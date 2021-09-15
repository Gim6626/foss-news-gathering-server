from django.contrib import admin

from tbot.models import *
from common.urlsbuilder import object_modification_url


class TelegramBotUserAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'tid',
        'username',
    )

    search_fields = (
        'tid',
        'username',
    )


class TelegramBotDigestRecordCategorizationAttemptAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'dt',
        'link_to_telegram_bot_user',
        'estimated_state',
        'link_to_digest_record',
        'estimated_is_main',
        'estimated_category',
        'estimated_subcategory',
    )

    autocomplete_fields = (
        'digest_record',
    )

    def link_to_digest_record(self, obj):
        return object_modification_url('gatherer', 'digestrecord', obj.digest_record.id, str(obj.digest_record))

    def link_to_telegram_bot_user(self, obj):
        return object_modification_url('tbot', 'telegrambotuser', obj.telegram_bot_user.id, str(obj.telegram_bot_user))


admin.site.register(TelegramBotUser, TelegramBotUserAdmin)
admin.site.register(TelegramBotDigestRecordCategorizationAttempt, TelegramBotDigestRecordCategorizationAttemptAdmin)
