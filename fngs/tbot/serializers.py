from rest_framework import serializers

from .models import *


class TelegramBotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramBotUser
        fields = [
            'id',
            'tid',
            'username',
            'groups',
        ]


class TelegramBotUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramBotUserGroup
        fields = [
            'id',
            'name',
            'users'
        ]


class TelegramBotUserGroupBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramBotUserGroup
        fields = [
            'id',
            'name',
        ]


class TelegramBotUserDetailedSerializer(serializers.ModelSerializer):
    groups = TelegramBotUserGroupBriefSerializer(many=True, read_only=True)

    class Meta:
        model = TelegramBotUser
        # depth = 1
        fields = [
            'id',
            'tid',
            'username',
            'groups',
        ]


class TelegramBotDigestRecordCategorizationAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramBotDigestRecordCategorizationAttempt
        fields = [
            'id',
            'dt',
            'telegram_bot_user',
            'digest_record',
            'estimated_state',
            'estimated_is_main',
            'estimated_content_type',
            'estimated_content_category',
        ]


class TelegramBotDigestRecordCategorizationAttemptDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramBotDigestRecordCategorizationAttempt
        depth = 1
        fields = [
            'id',
            'dt',
            'telegram_bot_user',
            'digest_record',
            'estimated_state',
            'estimated_is_main',
            'estimated_content_type',
            'estimated_content_category',
        ]