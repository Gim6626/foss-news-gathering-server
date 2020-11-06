from rest_framework import (
    permissions,
    viewsets,
)
from gatherer.serializers import *
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
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


class SpecificDigestRecordsViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    model = DigestRecord
    serializer_class = DigestRecordSerializer
    queryset = DigestRecord.objects.all()
    filter_class = SpecificDigestRecordsFilter
    filter_backends = [DjangoFilterBackend]
