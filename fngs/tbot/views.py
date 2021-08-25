import random
from rest_framework import (
    viewsets,
    permissions,
    mixins,
    status,
)
from rest_framework.response import Response

from gatherer.serializers import *
from common.permissions import *

from .models import *
from .serializers import *


class TelegramBotUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotUser.objects.all().order_by('username')
    serializer_class = TelegramBotUserSerializer


class TelegramBotDigestRecordCategorizationAttemptViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotDigestRecordCategorizationAttempt.objects.all().order_by('-dt')
    serializer_class = TelegramBotDigestRecordCategorizationAttemptSerializer


class TelegramBotDigestRecordCategorizationAttemptDetailedViewSet(mixins.ListModelMixin,
                                                                  mixins.RetrieveModelMixin,
                                                                  viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotDigestRecordCategorizationAttempt.objects.all().order_by('-dt')
    serializer_class = TelegramBotDigestRecordCategorizationAttemptDetailedSerializer


class TelegramBotOneRandomNotCategorizedFossNewsDigestRecordViewSet(mixins.ListModelMixin,
                                                                    mixins.RetrieveModelMixin,
                                                                    viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    serializer_class = DigestRecordSerializer

    ENOUGH_TBOT_USERS_DIGEST_RECORD_ESTIMATIONS = 3

    def get_queryset(self):
        tbot_user_id = self.request.query_params.get('tbot-user-id', None)
        if tbot_user_id is None:
            return []
        try:
            tbot_user = TelegramBotUser.objects.get(pk=tbot_user_id)
        except TelegramBotUser.DoesNotExist:
            return []
        categorized_by_this_user_digest_records_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(telegram_bot_user=tbot_user)
        not_categorized_by_this_user_digest_records = DigestRecord.objects.filter(state='UNKNOWN', projects__in=(Project.objects.filter(name='FOSS News'))).exclude(pk__in=[a.digest_record.pk for a in categorized_by_this_user_digest_records_attempts]).order_by('-dt')
        attempts_per_digest_record = {}
        for attempt in TelegramBotDigestRecordCategorizationAttempt.objects.all():
            if attempt.digest_record.id in attempts_per_digest_record:
                attempts_per_digest_record[attempt.digest_record.id] += 1
            else:
                attempts_per_digest_record[attempt.digest_record.id] = 1
        digest_records_with_enough_attempts = [drid
                                               for drid, attempts in attempts_per_digest_record.items()
                                               if attempts >= self.ENOUGH_TBOT_USERS_DIGEST_RECORD_ESTIMATIONS]
        not_categorized_by_this_user_digest_records_but_still_actual = not_categorized_by_this_user_digest_records.exclude(pk__in=digest_records_with_enough_attempts)
        if not_categorized_by_this_user_digest_records_but_still_actual:
            random_record = random.choice(not_categorized_by_this_user_digest_records_but_still_actual)
            return [random_record]
        else:
            return []


class TelegramBotUserByTidViewSet(mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]

    def list(self, request, *args, **kwargs):
        tid = request.query_params.get('tid', None)
        if not tid:
            return Response({'error': '"tid" option is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        telegram_bot_users = TelegramBotUser.objects.filter(tid=tid)
        if not telegram_bot_users:
            return Response({'error': 'Telegram bot users not found'},
                            status=status.HTTP_404_NOT_FOUND)
        telegram_bot_user = telegram_bot_users[0]
        return Response({
                            # TODO: Use serializer
                            'id': telegram_bot_user.id,
                            'tid': telegram_bot_user.tid,
                            'username': telegram_bot_user.username,
                        },
                        status=status.HTTP_200_OK)
