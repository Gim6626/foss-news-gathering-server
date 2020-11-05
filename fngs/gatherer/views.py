from django.shortcuts import render
from rest_framework import (
    permissions,
    viewsets,
    mixins,
    status,
    response,
)
from gatherer.models import *
from gatherer.serializers import *
from django.core import serializers
from django.http import JsonResponse


class DigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecord.objects.all().order_by('dt')
    serializer_class = DigestRecordSerializer


class NewDigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecord.objects.filter(state='UNKNOWN')
    serializer_class = DigestRecordSerializer


# TODO: Make it DRF style
def specific_digest_records(request, digest_id):
    records = list(DigestRecord.objects.filter(digest_number=digest_id).values())
    if records:
        return JsonResponse(data=records, safe=False, status=200)
    else:
        return JsonResponse(data=[], safe=False, status=404)
