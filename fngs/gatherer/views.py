import re

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from gatherer.serializers import *
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from gatherer.filters import *
from common.permissions import *
from tbot.models import *


class DigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecord.objects.all().order_by('dt')
    serializer_class = DigestRecordSerializer


class NewDigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecord.objects.filter(state='UNKNOWN')
    serializer_class = DigestRecordSerializer


class NewFossNewsDigestRecordViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]
    queryset = DigestRecord.objects.filter(state='UNKNOWN', projects__in=(Project.objects.filter(name='FOSS News')))
    serializer_class = DigestRecordDetailedSerializer


class OneNewFossNewsDigestRecordViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = DigestRecord.objects.filter(state='UNKNOWN', projects__in=(Project.objects.filter(name='FOSS News'))).order_by('dt')
        if queryset:
            return [queryset[0]]
        else:
            return []


class NotCategorizedDigestRecordsCountViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        count = len(DigestRecord.objects.filter(state='UNKNOWN', projects__in=(Project.objects.filter(name='FOSS News'))))
        return Response({'count': count}, status=status.HTTP_200_OK)


class SpecificDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    model = DigestRecord
    serializer_class = DigestRecordDetailedSerializer
    queryset = DigestRecord.objects.all()
    filter_class = SpecificDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


class DigestRecordDuplicateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecordDuplicate.objects.all()
    serializer_class = DigestRecordDuplicateSerializer


class DigestRecordDuplicateDetailedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecordDuplicate.objects.all()
    serializer_class = DigestRecordDuplicateDetailedSerializer
    filter_class = CurrentDigestRecordsDuplicatesFilter
    filter_backends = [DjangoFilterBackend]


class SimilarDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    model = DigestRecord
    serializer_class = DigestRecordSerializer
    queryset = DigestRecord.objects.filter(state='IN_DIGEST')
    filter_class = SimilarDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


class DuplicatesByDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    model = DigestRecordDuplicate
    serializer_class = DigestRecordDuplicateDetailedSerializer
    queryset = DigestRecordDuplicate.objects.all()
    filter_class = DuplicatesByDigestRecordFilter
    filter_backends = [DjangoFilterBackend]


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer


class DigestIssueViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestIssue.objects.all()
    serializer_class = DigestIssueSerializer


class GuessCategoryView(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]

    def list(self, request, *args, **kwargs):
        title = request.query_params.get('title', None)
        keywords = Keyword.objects.all()
        matched_keywords_by_category = {}
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword.name)}\b', title, re.IGNORECASE):
                if keyword.category not in matched_keywords_by_category:
                    matched_keywords_by_category[keyword.category] = []
                matched_keywords_by_category[keyword.category].append(keyword.name)
        return Response({'title': title, 'matches': matched_keywords_by_category}, status=status.HTTP_200_OK)


class SimilarRecordsInPreviousDigest(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]

    def list(self, request, *args, **kwargs):
        current_digest_number_str = request.query_params.get('current-digest-number', None)
        if not current_digest_number_str:
            return Response({'error': '"current-digest-number" option is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not current_digest_number_str.isdigit():
            return Response({'error': '"current-digest-number" option should be integer'},
                            status=status.HTTP_400_BAD_REQUEST)
        current_digest_number = int(current_digest_number_str)

        keywords_str = request.query_params.get('keywords', None)
        if not keywords_str:
            return Response({'error': '"keywords" option is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        keywords = keywords_str.split(',')

        similar_records_in_previous_digest = []
        for keyword in keywords:
            records = DigestRecord.objects.filter(digest_number=current_digest_number - 1, state='IN_DIGEST')
            for record in records:
                if re.search(rf'\b{re.escape(keyword)}\b', record.title, re.IGNORECASE):
                    similar_records_in_previous_digest.append(record)
        similar_records_in_previous_digest_titles = [
            {
                # TODO: Use serializer
                'title': r.title,
                'is_main': r.is_main,
                'category': r.category,
                'subcategory': r.subcategory,
            }
            for r in similar_records_in_previous_digest
        ]

        return Response({'similar_records_in_previous_digest': similar_records_in_previous_digest_titles},
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
                    'digest_issue': categorization_attempt.digest_record.digest_issue,
                    'is_main': categorization_attempt.digest_record.is_main,
                    'category': categorization_attempt.digest_record.category,
                    'subcategory': categorization_attempt.digest_record.subcategory,
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
