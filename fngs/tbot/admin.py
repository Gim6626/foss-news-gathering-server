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
        'links_to_groups',
    )

    search_fields = (
        'tid',
        'username',
    )

    def links_to_groups(self, obj):
        return object_modification_url('tbot', 'telegrambotusergroup', [g.id for g in obj.groups.all()], [str(g) for g in obj.groups.all()])


class TelegramBotUserGroupAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'name',
        'links_to_users',
    )

    search_fields = (
        'id',
        'name',
    )

    def links_to_users(self, obj):
        return object_modification_url('tbot', 'telegrambotuser', [u.id for u in obj.users.all()], [str(u) for u in obj.users.all()])


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
        'estimated_content_type',
        'estimated_content_category',
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
admin.site.register(TelegramBotUserGroup, TelegramBotUserGroupAdmin)
