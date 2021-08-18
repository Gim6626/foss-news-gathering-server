from rest_framework import (
    viewsets,
    permissions,
    mixins,
)

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


class TelegramBotNotCategorizedFossNewsDigestRecordsViewSet(mixins.ListModelMixin,
                                                            mixins.RetrieveModelMixin,
                                                            viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    serializer_class = DigestRecordSerializer

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
        return not_categorized_by_this_user_digest_records
