import random

from rest_framework.decorators import action
from django.forms.models import model_to_dict
from rest_framework import (
    viewsets,
    permissions,
    mixins,
    status,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from gatherer.serializers import *
from gatherer.mixins import *
from common.permissions import *

from .models import *
from .serializers import *


class TelegramBotUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]
    queryset = TelegramBotUser.objects.all().order_by('username')
    serializer_class = TelegramBotUserSerializer

    def list(self, request, *args, **kwargs):
        tid = request.query_params.get('tid', None)
        if tid:
            telegram_bot_users = TelegramBotUser.objects.filter(tid=tid)
            if not telegram_bot_users:
                return Response({'error': f'Telegram bot user with tid="{tid}" not found'},
                                status=status.HTTP_404_NOT_FOUND)
            telegram_bot_user = telegram_bot_users[0]
            return Response(TelegramBotUserDetailedSerializer(telegram_bot_user).data,
                            status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='detailed')
    def detailed_list(self, request, *args, **kwargs):
        data = TelegramBotUserDetailedSerializer(self.paginate_queryset(self.queryset), many=True).data
        return self.get_paginated_response(data)

    @action(detail=True, methods=['get'], url_path='detailed')
    def detailed_one(self, request, *args, **kwargs):
        data = TelegramBotUserDetailedSerializer(self.get_object()).data
        return Response(data,
                        status=status.HTTP_200_OK)


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

    def not_categorized_records(self, tbot_user_id, project_name='FOSS News'):
        if tbot_user_id is None:
            return []
        try:
            tbot_user = TelegramBotUser.objects.get(pk=tbot_user_id)
        except TelegramBotUser.DoesNotExist:
            return []
        categorized_by_this_user_digest_records_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(telegram_bot_user=tbot_user)
        not_categorized_by_this_user_digest_records = DigestRecord.objects.filter(state='UNKNOWN',
                                                                                  projects__in=(Project.objects.filter(name=project_name))).exclude(pk__in=[a.digest_record.pk for a in categorized_by_this_user_digest_records_attempts]).order_by('-dt')
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


# TODO: Obsolete, remove with removal of api/v1
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


class TelegramBotOneRandomNotCategorizedDigestRecordViewSet(mixins.ListModelMixin,
                                                            viewsets.GenericViewSet,
                                                            NotCategorizedFossNewsDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]

    queryset = []

    def list(self, request, *args, **kwargs):
        tbot_user_id = request.query_params.get('tbot-user-id', None)
        if not tbot_user_id:
            return Response({'error': 'Empty "tbot-user-id" parameter'}, status=status.HTTP_400_BAD_REQUEST)
        project_name = self.request.query_params.get('project', None)
        if not project_name:
            return Response({'error': 'Empty "project_name" parameter'}, status=status.HTTP_400_BAD_REQUEST)
        not_categorized_by_this_user_digest_records_but_still_actual = self.not_categorized_records(tbot_user_id,
                                                                                                    project_name)
        if not_categorized_by_this_user_digest_records_but_still_actual:
            random_record = random.choice(not_categorized_by_this_user_digest_records_but_still_actual)
            return Response({'results': [DigestRecordDetailedSerializer(random_record).data]}, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


# TODO: Obsolete, remove with removal of api/v1
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


class TelegramBotNotCategorizedDigestRecordsCountViewSet(mixins.ListModelMixin,
                                                         viewsets.GenericViewSet,
                                                         NotCategorizedFossNewsDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotFullPermission]

    def list(self, request, *args, **kwargs):
        tbot_user_id = request.query_params.get('tbot-user-id', None)
        if not tbot_user_id:
            return Response({'error': 'Empty "tbot-user-id" parameter'}, status=status.HTTP_400_BAD_REQUEST)
        project_name = self.request.query_params.get('project', None)
        if not project_name:
            return Response({'error': 'Empty "project_name" parameter'}, status=status.HTTP_400_BAD_REQUEST)
        not_categorized_by_this_user_digest_records_but_still_actual = self.not_categorized_records(tbot_user_id,
                                                                                                    project_name)
        if not_categorized_by_this_user_digest_records_but_still_actual:
            return Response({'count': not_categorized_by_this_user_digest_records_but_still_actual.count()}, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


# TODO: Obsolete, remove with removal of api/v1
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
        return Response(TelegramBotUserDetailedSerializer(telegram_bot_user).data,
                        status=status.HTTP_200_OK)


class DigestRecordsCategorizedByTbotViewSet(mixins.ListModelMixin,
                                            GenericViewSet,
                                            NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        not_fully_categorized_digest_records = self.not_categorized_records_queryset(from_bot=True)
        tbot_categorizations_attempts_for_unknown_records = TelegramBotDigestRecordCategorizationAttempt.objects.filter(digest_record__in=not_fully_categorized_digest_records)
        categorizations_data_by_digest_record = {}
        categorization_attempt: TelegramBotDigestRecordCategorizationAttempt
        for categorization_attempt in tbot_categorizations_attempts_for_unknown_records:
            digest_record_id = categorization_attempt.digest_record.id
            if digest_record_id not in categorizations_data_by_digest_record:
                categorizations_data_by_digest_record[digest_record_id] = {
                    'record': DigestRecordDetailedSerializer(DigestRecord.objects.get(id=digest_record_id)).data,
                    'estimations': [],
                }
            estimation_data = {
                'user': categorization_attempt.telegram_bot_user.username,
                'state': categorization_attempt.estimated_state,
                'is_main': categorization_attempt.estimated_is_main,
                'content_type': categorization_attempt.estimated_content_type,
                'content_category': categorization_attempt.estimated_content_category,
            }
            categorizations_data_by_digest_record[digest_record_id]['estimations'].append(estimation_data)
        return Response(categorizations_data_by_digest_record,
                        status=status.HTTP_200_OK)
