from django.db.models import Q

import datetime
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


class NotCategorizedDigestRecordsMixin:

    def not_categorized_records_queryset(self):
        queryset1 = DigestRecord.objects.filter(state='UNKNOWN', projects__in=(Project.objects.filter(name='FOSS News')))
        queryset2 = DigestRecord.objects.filter(digest_issue__number=DigestIssue.objects.order_by('-number')[0].number, state='IN_DIGEST', projects__in=(Project.objects.filter(name='FOSS News'))).filter(~Q(content_type=None))
        return queryset1 | queryset2


class NewFossNewsDigestRecordViewSet(GenericViewSet,
                                     mixins.ListModelMixin,
                                     NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = self.not_categorized_records_queryset()
        return queryset


class OneNewFossNewsDigestRecordViewSet(GenericViewSet,
                                        mixins.ListModelMixin,
                                        NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = self.not_categorized_records_queryset()
        queryset = queryset.order_by('dt')
        if queryset:
            return [queryset[0]]
        else:
            return []


class NotCategorizedDigestRecordsFromTbotMixin(NotCategorizedDigestRecordsMixin):

    def not_categorized_records_queryset(self):
        queryset = super().not_categorized_records_queryset()
        dt_now = datetime.datetime.now()
        dt_now_minus_2w = dt_now - datetime.timedelta(days=14)
        recent_tbot_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(dt__gt=dt_now_minus_2w)
        recent_tbot_attempts_records_ids = [attempt.digest_record.id for attempt in recent_tbot_attempts]
        queryset = queryset.filter(id__in=recent_tbot_attempts_records_ids)
        return queryset


class OneNewFossNewsDigestRecordFromTbotViewSet(GenericViewSet,
                                                mixins.ListModelMixin,
                                                NotCategorizedDigestRecordsFromTbotMixin):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = self.not_categorized_records_queryset()
        queryset = queryset.order_by('dt')
        if queryset:
            return [queryset[0]]
        else:
            return []


class NotCategorizedDigestRecordsCountViewSet(mixins.ListModelMixin,
                                              GenericViewSet,
                                              NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.not_categorized_records_queryset()
        count = queryset.count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class NotCategorizedDigestRecordsFromTbotCountViewSet(mixins.ListModelMixin,
                                                      GenericViewSet,
                                                      NotCategorizedDigestRecordsFromTbotMixin):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.not_categorized_records_queryset()
        count = queryset.count()
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


class GuessContentCategoryView(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]

    def list(self, request, *args, **kwargs):
        title = request.query_params.get('title', None)
        keywords = Keyword.objects.all()
        matched_keywords_by_content_category = {}
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword.name)}\b', title, re.IGNORECASE):
                if keyword.content_category not in matched_keywords_by_content_category:
                    matched_keywords_by_content_category[keyword.content_category] = []
                matched_keywords_by_content_category[keyword.content_category].append(keyword.name)
        return Response({'title': title, 'matches': matched_keywords_by_content_category}, status=status.HTTP_200_OK)


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
            records = DigestRecord.objects.filter(digest_issue__number=current_digest_number - 1, state='IN_DIGEST')
            for record in records:
                if re.search(rf'\b{re.escape(keyword)}\b', record.title, re.IGNORECASE) and record not in similar_records_in_previous_digest:
                    similar_records_in_previous_digest.append(record)
        similar_records_in_previous_digest_titles = [DigestRecordDetailedSerializer(r).data
                                                     for r in similar_records_in_previous_digest]

        return Response({'similar_records_in_previous_digest': similar_records_in_previous_digest_titles},
                        status=status.HTTP_200_OK)
