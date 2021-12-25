from rest_framework import serializers

from gatherer.models import *


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


class DigestRecordSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        # TODO: Extract common code from here and DigestRecordDetailedSerializer
        representation = super().to_representation(instance)
        representation['dt'] = instance.dt.strftime(DATETIME_FORMAT) if instance.dt else None
        representation['gather_dt'] = instance.gather_dt.strftime(DATETIME_FORMAT) if instance.gather_dt else None
        return representation

    class Meta:
        model = DigestRecord
        fields = [
            'id',
            'dt',
            'gather_dt',
            'source',
            'title',
            'url',
            'additional_url',
            'state',
            'digest_issue',
            'is_main',
            'content_type',
            'content_category',
            'title_keywords',
            'projects',
            'language',
        ]


class SimilarDigestRecordsSerializer(serializers.ModelSerializer):
    digest_records = DigestRecordSerializer(many=True)

    class Meta:
        model = SimilarDigestRecords
        fields = [
            'id',
            'digest_issue',
            'digest_records',
        ]


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'records',
        ]


class KeywordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Keyword
        fields = [
            'id',
            'name',
            'content_category',
            'is_generic',
            'proprietary',
            'enabled',
        ]


class DigestRecordDetailedSerializer(serializers.ModelSerializer):
    not_proprietary_keywords = KeywordSerializer(many=True, read_only=True)
    proprietary_keywords = KeywordSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        # TODO: Extract common code from here and DigestRecordSerializer
        representation = super().to_representation(instance)
        representation['dt'] = instance.dt.strftime(DATETIME_FORMAT) if instance.dt else None
        representation['gather_dt'] = instance.gather_dt.strftime(DATETIME_FORMAT) if instance.gather_dt else None
        return representation

    class Meta:
        model = DigestRecord
        depth = 2
        fields = [
            'id',
            'dt',
            'gather_dt',
            'source',
            'title',
            'url',
            'additional_url',
            'state',
            'digest_issue',
            'is_main',
            'content_type',
            'content_category',
            'title_keywords',
            'not_proprietary_keywords',
            'proprietary_keywords',
            'projects',
            'language',
            'tbot_estimations',
        ]


class SimilarDigestRecordsDetailedSerializer(serializers.ModelSerializer):
    digest_records = DigestRecordDetailedSerializer(many=True, read_only=True)

    class Meta:
        model = SimilarDigestRecords
        depth = 2
        fields = [
            'id',
            'digest_issue',
            'digest_records',
        ]


class DigestRecordSimplifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = DigestRecord
        fields = [
            'id',
            'dt',
            'gather_dt',
            'source',
            'title',
            'url',
            'additional_url',
        ]


class SimilarDigestRecordsSimplifiedSerializer(serializers.ModelSerializer):
    digest_records = DigestRecordSimplifiedSerializer(many=True, read_only=True)

    class Meta:
        model = SimilarDigestRecords
        depth = 2
        fields = [
            'id',
            'digest_issue',
            'digest_records',
        ]


class DigestRecordWithSimilarSerializer(serializers.ModelSerializer):
    similar_records = SimilarDigestRecordsSimplifiedSerializer(many=True, read_only=True)

    class Meta:
        model = DigestRecord
        depth = 2
        fields = [
            'id',
            'title',
            'url',
            'additional_url',
            'similar_records',
        ]


class DigestIssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = DigestIssue
        fields = [
            'id',
            'number',
            'is_special',
            'habr_url',
        ]
