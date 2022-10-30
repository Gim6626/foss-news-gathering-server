import datetime
import re

from rest_framework.decorators import action
from rest_framework import (
    viewsets,
    mixins,
    status,
)

import fngs.pagination
from gatherer.serializers import *
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from gatherer.filters import *
from common.permissions import *
from gatherer.mixins import *
from tbot.models import *


class DigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecord.objects.all().order_by('dt')
    serializer_class = DigestRecordSerializer

    @action(detail=False, methods=['get'], url_path='detailed')
    def detailed_list(self, request, *args, **kwargs):
        queryset = self.queryset
        digest_issue = request.query_params.get('digest_issue', None)
        if digest_issue is not None:
            queryset = queryset.filter(digest_issue=digest_issue)
        data = DigestRecordDetailedSerializer(self.paginate_queryset(queryset), many=True).data
        return self.get_paginated_response(data)

    @action(detail=True, methods=['get'], url_path='detailed')
    def detailed_one(self, request, *args, **kwargs):
        data = DigestRecordDetailedSerializer(self.get_object()).data
        return Response(data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='similar')
    def similar(self, request, *args, **kwargs):
        queryset = self.queryset.filter(state='IN_DIGEST')
        digest_issue = request.query_params.get('digest_issue', None)
        if digest_issue is not None:
            queryset = queryset.filter(digest_issue=digest_issue)
        content_type = request.query_params.get('content_type', None)
        if content_type is not None:
            queryset = queryset.filter(content_type=content_type)
        content_category = request.query_params.get('content_category', None)
        if content_category is not None:
            queryset = queryset.filter(content_category=content_category)
        data = DigestRecordWithSimilarSerializer(self.paginate_queryset(queryset), many=True).data
        return self.get_paginated_response(data)


# TODO: Obsolete, remove with removal of api/v1
class DetailedDigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecord.objects.all().order_by('dt')
    serializer_class = DigestRecordDetailedSerializer
    model = DigestRecord
    filter_class = SpecificDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


# TODO: Obsolete, remove with removal of api/v1
class NewDigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = DigestRecord.objects.filter(state='UNKNOWN')
    serializer_class = DigestRecordSerializer


# TODO: Obsolete, remove with removal of api/v1
class NewFossNewsDigestRecordViewSet(GenericViewSet,
                                     mixins.ListModelMixin,
                                     NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = self.not_categorized_records_queryset(from_bot=False)
        return queryset


class NotCategorizedDigestRecordViewSet(GenericViewSet,
                                        mixins.ListModelMixin,
                                        NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]
    serializer_class = DigestRecordDetailedSerializer

    def list(self, request, *args, **kwargs):
        project_name = request.query_params.get('project', None)
        if not project_name:
            return Response({'error': 'Missing "project" option'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.not_categorized_records_queryset(from_bot=False, project_name=project_name)
        return Response(DigestRecordSerializer(queryset).data, status=status.HTTP_200_OK)


# TODO: Obsolete, remove with removal of api/v1
class OneNewFossNewsDigestRecordViewSet(GenericViewSet,
                                        mixins.ListModelMixin,
                                        NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = self.not_categorized_records_queryset(from_bot=False)
        queryset = queryset.order_by('dt')
        if queryset:
            return [queryset[0]]
        else:
            return []


class OldestNotCategorizedDigestRecordViewSet(GenericViewSet,
                                              mixins.ListModelMixin,
                                              NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DigestRecordDetailedSerializer

    queryset = []

    def list(self, request, *args, **kwargs):
        project_name = request.query_params.get('project', None)
        if not project_name:
            return Response({'error': 'Missing "project" option'}, status=status.HTTP_400_BAD_REQUEST)
        from_bot = request.query_params.get('from-bot', None)
        if not from_bot:
            return Response({'error': 'Missing "from-bot" option'}, status=status.HTTP_400_BAD_REQUEST)
        from_bot = False if from_bot.lower() == 'false' else True
        queryset = self.not_categorized_records_queryset(from_bot, project_name)
        queryset = queryset.order_by('dt')
        if queryset:
            digest_record = queryset[0]
            return Response({
                                'results': [DigestRecordDetailedSerializer(digest_record).data],
                                'links': {
                                    'next': None,
                                },
                            },
                            status=status.HTTP_200_OK)
        else:
            return Response({
                                'results': [],
                                'links': {
                                    'next': None,
                                },
                            },
                            status=status.HTTP_200_OK)


# TODO: Obsolete, remove with removal of api/v1
class OneNewFossNewsDigestRecordFromTbotViewSet(GenericViewSet,
                                                mixins.ListModelMixin,
                                                NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DigestRecordDetailedSerializer

    def get_queryset(self):
        queryset = self.not_categorized_records_queryset(from_bot=True)
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
        project_name = request.query_params.get('project', None)
        if project_name is None:
            return Response({'error': 'Missing "project" option'}, status=status.HTTP_400_BAD_REQUEST)
        from_bot = request.query_params.get('from-bot', None)
        if from_bot is None:
            return Response({'error': 'Missing "from-bot" option'}, status=status.HTTP_400_BAD_REQUEST)
        from_bot = from_bot == 'true'
        queryset = self.not_categorized_records_queryset(from_bot=from_bot, project_name=project_name)
        count = queryset.count()
        return Response({'count': count}, status=status.HTTP_200_OK)


# TODO: Obsolete, remove with removal of api/v1
class NotCategorizedDigestRecordsFromTbotCountViewSet(mixins.ListModelMixin,
                                                      GenericViewSet,
                                                      NotCategorizedDigestRecordsMixin):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.not_categorized_records_queryset(from_bot=True)
        count = queryset.count()
        return Response({'count': count}, status=status.HTTP_200_OK)


# TODO: Obsolete, remove with removal of api/v1
class SpecificDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    model = DigestRecord
    serializer_class = DigestRecordDetailedSerializer
    queryset = DigestRecord.objects.all()
    filter_class = SpecificDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


class SimilarDigestRecordsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = SimilarDigestRecords.objects.all()
    serializer_class = SimilarDigestRecordsSerializer

    @action(detail=False, methods=['get'], url_path='detailed')
    def detailed_list(self, request, *args, **kwargs):
        queryset = self.queryset
        digest_issue = request.query_params.get('digest_issue', None)
        if digest_issue is not None:
            queryset = queryset.filter(digest_issue=digest_issue)
        digest_record = request.query_params.get('digest_record', None)
        if digest_record is not None:
            queryset = queryset.filter(digest_records__in=digest_record)
        data = SimilarDigestRecordsDetailedSerializer(self.paginate_queryset(queryset), many=True).data
        return self.get_paginated_response(data)

    @action(detail=True, methods=['get'], url_path='detailed')
    def detailed_one(self, request, *args, **kwargs):
        data = SimilarDigestRecordsDetailedSerializer(self.get_object()).data
        return Response(data,
                        status=status.HTTP_200_OK)


# TODO: Obsolete, remove with removal of api/v1
class SimilarDigestRecordsDetailedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = SimilarDigestRecords.objects.all()
    serializer_class = SimilarDigestRecordsDetailedSerializer
    filter_class = SimilarDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


# TODO: Obsolete, remove with removal of api/v1
class DigestRecordsLookingSimilarViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    model = DigestRecord
    serializer_class = DigestRecordWithSimilarSerializer
    queryset = DigestRecord.objects.filter(state='IN_DIGEST')
    filter_class = DigestRecordsLookingSimilarFilter
    filter_backends = [DjangoFilterBackend]


# TODO: Obsolete, remove with removal of api/v1
class SimilarDigestRecordsByDigestRecordViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAdminUser]
    model = SimilarDigestRecords
    serializer_class = SimilarDigestRecordsDetailedSerializer
    queryset = SimilarDigestRecords.objects.all()
    filter_class = SimilarDigestRecordsByDigestRecordFilter
    filter_backends = [DjangoFilterBackend]


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class KeywordPagination(fngs.pagination.Pagination):
    max_page_size = 5000


class KeywordViewSet(viewsets.ModelViewSet):
    pagination_class = KeywordPagination
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


class SimilarRecordsInPreviousNonSpecialDigest(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAdminUser | TelegramBotReadOnlyPermission]

    queryset = []

    def list(self, request, *args, **kwargs):
        digest_number_str = kwargs.get('digest_number', None)
        if not digest_number_str:
            return Response({'error': '"digest_number_str" option is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not digest_number_str.isdigit():
            return Response({'error': '"digest_number_str" option should be integer'},
                            status=status.HTTP_400_BAD_REQUEST)
        digest_number = int(digest_number_str)

        keywords_str = request.query_params.get('keywords', None)
        if not keywords_str:
            return Response({'error': '"keywords" option is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        keywords = keywords_str.split(',')

        similar_records_in_previous_digest = []
        for keyword in keywords:
            i = digest_number
            while True:
                previous_digest_issues = DigestIssue.objects.filter(number=i - 1)
                if not previous_digest_issues:
                    return DigestRecordsSource({'error': 'bad digest number'},
                                               status=status.HTTP_400_BAD_REQUEST)
                previous_digest_issue = previous_digest_issues[0]
                if not previous_digest_issue.is_special:
                    break
                else:
                    i -= 1
            records = DigestRecord.objects.filter(digest_issue=previous_digest_issue, state='IN_DIGEST')
            for record in records:
                if re.search(rf'\b{re.escape(keyword)}\b', record.title, re.IGNORECASE) and record not in similar_records_in_previous_digest:
                    similar_records_in_previous_digest.append(record)
        similar_records_in_previous_digest_titles = [DigestRecordDetailedSerializer(r).data
                                                     for r in similar_records_in_previous_digest]

        return Response(similar_records_in_previous_digest_titles,
                        status=status.HTTP_200_OK)


# TODO: Obsolete, remove with removal of api/v1 by adding search by keywords to DigestRecordsLookingSimilarFilter
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
