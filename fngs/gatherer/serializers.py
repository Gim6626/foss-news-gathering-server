from rest_framework import serializers

from gatherer.models import *


class DigestRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigestRecord
        fields = [
            'id',
            'dt',
            'gather_dt',
            'title',
            'url',
            'state',
            'digest_number',
            'is_main',
            'category',
            'subcategory',
        ]
