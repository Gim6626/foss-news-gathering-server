from rest_framework import serializers

from gatherer.models import *


class DigestRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigestRecord
        fields = [
            'id',
            'dt',
            'title',
            'url',
        ]
