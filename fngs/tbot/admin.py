from django.contrib import admin

from tbot.models import *


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
        'telegram_bot_user',
        'digest_record',
        'estimated_state',
        'estimated_is_main',
        'estimated_category',
        'estimated_subcategory',
    )
    autocomplete_fields = (
        'digest_record',
    )

admin.site.register(TelegramBotUser, TelegramBotUserAdmin)
admin.site.register(TelegramBotDigestRecordCategorizationAttempt, TelegramBotDigestRecordCategorizationAttemptAdmin)
