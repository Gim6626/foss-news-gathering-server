import datetime

from django.urls import reverse
from django.contrib import admin

from gatherer.models import *
from common.urlsbuilder import object_modification_url


class DigestRecordAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )
    list_display = (
        'id',
        'dt',
        'link_to_source',
        'gather_dt',
        'title',
        'url',
        'additional_url',
        'state',
        'link_to_digest_issue',
        'is_main',
        'content_type',
        'content_category',
        'language',
        'similar_records',
        'links_to_projects',
        'links_to_keywords',
    )

    filter_horizontal = (
        'title_keywords',
    )

    search_fields = (
        'title',
        'url',
    )

    autocomplete_fields = (
        'digest_issue',
    )

    def link_to_source(self, obj):
        return object_modification_url('gatherer', 'digestrecordssource', obj.source.id if obj.source else None, str(obj.source))

    def link_to_digest_issue(self, obj):
        return object_modification_url('gatherer', 'digestissue', obj.digest_issue.id if obj.digest_issue else None, str(obj.digest_issue))

    def links_to_projects(self, obj):
        return object_modification_url('gatherer', 'project', [p.id for p in obj.projects.all()], [str(p) for p in obj.projects.all()])

    def links_to_keywords(self, obj):
        return object_modification_url('gatherer', 'keyword', [k.id for k in obj.title_keywords.all()], [str(k) for k in obj.title_keywords.all()])


class SimilarDigestRecordsAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'digest_number',
        'link_to_digest_issue',
        'digest_records_titles',
    )

    filter_horizontal = (
        'digest_records',
    )

    autocomplete_fields = (
        'digest_issue',
    )

    def link_to_digest_issue(self, obj):
        return object_modification_url('gatherer', 'digestissue', obj.digest_issue.id if obj.digest_issue else None, str(obj.digest_issue))

    def get_field_queryset(self, db, db_field, request):
        if db_field.name == 'digest_records':
            foss_news_project = Project.objects.filter(name='FOSS News')
            queryset = DigestRecord.objects.filter(projects__in=(foss_news_project),
                                                   state=DigestRecordState.IN_DIGEST.name,
                                                   gather_dt__gt=datetime.datetime.now() - datetime.timedelta(14))
            return queryset
        else:
            super().get_field_queryset(db, db_field, request)


class ProjectAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'name',
    )


class KeywordAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'name',
        'content_category',
        'is_generic',
        'proprietary',
        'enabled',
    )

    search_fields = (
        'name',
    )


class DigestRecordsSourceAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'name',
        'enabled',
        'data_url',
        'links_to_projects',
        'language',
    )

    search_fields = (
        'name',
    )

    def links_to_projects(self, obj):
        return object_modification_url('gatherer', 'project', [p.id for p in obj.projects.all()], [str(p) for p in obj.projects.all()])


class DigestIssueAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'number',
        'is_special',
        'habr_url',
    )

    search_fields = (
        'number',
    )


class DigestGatheringIterationAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'dt',
        'overall_count',
        'gathered_count',
        'saved_count',
        'link_to_source',
        'source_enabled',
        'source_error',
        'parser_error',
    )

    autocomplete_fields = (
        'source',
    )

    def link_to_source(self, obj):
        return object_modification_url('gatherer', 'digestrecordssource', obj.source.id if obj.source else None, str(obj.source))


admin.site.register(DigestRecord, DigestRecordAdmin)
admin.site.register(SimilarDigestRecords, SimilarDigestRecordsAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(DigestRecordsSource, DigestRecordsSourceAdmin)
admin.site.register(DigestIssue, DigestIssueAdmin)
admin.site.register(DigestGatheringIteration, DigestGatheringIterationAdmin)
