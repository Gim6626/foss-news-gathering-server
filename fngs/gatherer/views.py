from django.shortcuts import render

from rest_framework import permissions, viewsets

from gatherer.models import *
from gatherer.serializers import *


class DigestRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DigestRecord.objects.all().order_by('dt')
    serializer_class = DigestRecordSerializer
