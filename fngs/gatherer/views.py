import re

from rest_framework import (
    permissions,
    viewsets,
    mixins,
    status,
)
from gatherer.serializers import *
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from gatherer.filters import *


class DigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecord.objects.all().order_by('dt')
    serializer_class = DigestRecordSerializer


class NewDigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecord.objects.filter(state='UNKNOWN')
    serializer_class = DigestRecordSerializer


class NewFossNwesDigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecord.objects.filter(state='UNKNOWN', projects__in=(Project.objects.filter(name='FOSS News')))
    serializer_class = DigestRecordSerializer


class SpecificDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    model = DigestRecord
    serializer_class = DigestRecordSerializer
    queryset = DigestRecord.objects.all()
    filter_class = SpecificDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


class DigestRecordDuplicateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecordDuplicate.objects.all()
    serializer_class = DigestRecordDuplicateSerializer


class DigestRecordDuplicateDetailedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecordDuplicate.objects.all()
    serializer_class = DigestRecordDuplicateDetailedSerializer
    filter_class = CurrentDigestRecordsDuplicatesFilter
    filter_backends = [DjangoFilterBackend]


class SimilarDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    model = DigestRecord
    serializer_class = DigestRecordSerializer
    queryset = DigestRecord.objects.filter(state='IN_DIGEST')
    filter_class = SimilarDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]


class DuplicatesByDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    model = DigestRecordDuplicate
    serializer_class = DigestRecordDuplicateDetailedSerializer
    queryset = DigestRecordDuplicate.objects.all()
    filter_class = DuplicatesByDigestRecordFilter
    filter_backends = [DjangoFilterBackend]


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer


class GuessCategoryView(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

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
