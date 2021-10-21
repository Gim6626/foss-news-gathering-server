import random
from rest_framework import (
    viewsets,
    permissions,
    mixins,
    status,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from gatherer.serializers import *
from common.permissions import *

from .models import *
from .serializers import *


class TelegramBotUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotUser.objects.all().order_by('username')
    serializer_class = TelegramBotUserSerializer


class TelegramBotUserDetailedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotUser.objects.all().order_by('username')
    serializer_class = TelegramBotUserDetailedSerializer


class TelegramBotUserGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotUserGroup.objects.all().order_by('name')
    serializer_class = TelegramBotUserGroupSerializer


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


class NotCategorizedFossNewsDigestRecordsMixin:

    ENOUGH_TBOT_USERS_DIGEST_RECORD_ESTIMATIONS = 3

    def not_categorized_records(self, tbot_user_id):
        if tbot_user_id is None:
            return []
        try:
            tbot_user = TelegramBotUser.objects.get(pk=tbot_user_id)
        except TelegramBotUser.DoesNotExist:
            return []
        categorized_by_this_user_digest_records_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(telegram_bot_user=tbot_user)
        not_categorized_by_this_user_digest_records = DigestRecord.objects.filter(state='UNKNOWN',
                                                                                  projects__in=(Project.objects.filter(name='FOSS News'))).exclude(pk__in=[a.digest_record.pk for a in categorized_by_this_user_digest_records_attempts]).order_by('-dt')
        attempts_for_not_categorized_records = TelegramBotDigestRecordCategorizationAttempt.objects.filter(digest_record__in=not_categorized_by_this_user_digest_records)
        attempts_per_digest_record = {}
        for attempt in attempts_for_not_categorized_records:
            if attempt.digest_record.id in attempts_per_digest_record:
                attempts_per_digest_record[attempt.digest_record.id] += 1
            else:
                attempts_per_digest_record[attempt.digest_record.id] = 1
        digest_records_with_enough_attempts = [drid
                                               for drid, attempts in attempts_per_digest_record.items()
                                               if attempts >= self.ENOUGH_TBOT_USERS_DIGEST_RECORD_ESTIMATIONS]
        not_categorized_by_this_user_digest_records_but_still_actual = not_categorized_by_this_user_digest_records.exclude(pk__in=digest_records_with_enough_attempts)
        return not_categorized_by_this_user_digest_records_but_still_actual


class TelegramBotOneRandomNotCategorizedFossNewsDigestRecordViewSet(mixins.ListModelMixin,
                                                                    mixins.RetrieveModelMixin,
                                                                    viewsets.GenericViewSet,
                                                                    NotCategorizedFossNewsDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        tbot_user_id = self.request.query_params.get('tbot-user-id', None)
        not_categorized_by_this_user_digest_records_but_still_actual = self.not_categorized_records(tbot_user_id)
        if not_categorized_by_this_user_digest_records_but_still_actual:
            random_record = random.choice(not_categorized_by_this_user_digest_records_but_still_actual)
            return [random_record]
        else:
            return []


class TelegramBotNotCategorizedFossNewsDigestRecordsCountViewSet(mixins.ListModelMixin,
                                                                 viewsets.GenericViewSet,
                                                                 NotCategorizedFossNewsDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]

    def list(self, request, *args, **kwargs):
        tbot_user_id = request.query_params.get('tbot-user-id', None)
        not_categorized_by_this_user_digest_records_but_still_actual = self.not_categorized_records(tbot_user_id)
        if not_categorized_by_this_user_digest_records_but_still_actual:
            return Response({'count': not_categorized_by_this_user_digest_records_but_still_actual.count()}, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


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


class DigestRecordsCategorizedByTbotViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        unknown_state_digest_records = DigestRecord.objects.filter(state='UNKNOWN')
        tbot_categorizations_attempts_for_unknown_records = TelegramBotDigestRecordCategorizationAttempt.objects.filter(digest_record__in=unknown_state_digest_records)
        categorizations_data_by_digest_record = {}
        for categorization_attempt in tbot_categorizations_attempts_for_unknown_records:
            digest_record_id = categorization_attempt.digest_record.id
            if digest_record_id not in categorizations_data_by_digest_record:
                categorizations_data_by_digest_record[digest_record_id] = {
                    # TODO: Use serializer
                    'dt': categorization_attempt.digest_record.dt,
                    'source': categorization_attempt.digest_record.source.name,
                    'title': categorization_attempt.digest_record.title,
                    'url': categorization_attempt.digest_record.url,
                    'additional_url': categorization_attempt.digest_record.additional_url,
                    'digest_issue': categorization_attempt.digest_record.digest_issue,
                    'is_main': categorization_attempt.digest_record.is_main,
                    'content_type': categorization_attempt.digest_record.content_type,
                    'content_category': categorization_attempt.digest_record.content_category,
                    'title_keywords': [k.name for k in categorization_attempt.digest_record.title_keywords.all()],
                    'estimations': [],
                }
            estimation_data = {
                'user': categorization_attempt.telegram_bot_user.username,
                'state': categorization_attempt.estimated_state,
            }
            categorizations_data_by_digest_record[digest_record_id]['estimations'].append(estimation_data)
        return Response(categorizations_data_by_digest_record,
                        status=status.HTTP_200_OK)
