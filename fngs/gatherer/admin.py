from django.contrib import admin

from gatherer.models import *


class DigestRecordAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
    )
    list_display = (
        'id',
        'dt',
        'source',
        'gather_dt',
        'title',
        'url',
        'state',
        'digest_number',
        'is_main',
        'category',
        'subcategory',
        'keywords',
        'language',
        'duplicates',
        'projects_names',
    )
    search_fields = (
        'title',
        'url',
    )


class DigestRecordDuplicateAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
    )
    list_display = (
        'id',
        'digest_number',
        'digest_records_titles',
    )
    filter_horizontal = (
        'digest_records',
    )


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
        'category',
        'is_generic',
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
    )

    search_fields = (
        'name',
    )


class DigestIssueAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )

    list_display = (
        'id',
        'number',
        'habr_url',
    )

    search_fields = (
        'number',
    )


admin.site.register(DigestRecord, DigestRecordAdmin)
admin.site.register(DigestRecordDuplicate, DigestRecordDuplicateAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(DigestRecordsSource, DigestRecordsSourceAdmin)
admin.site.register(DigestIssue, DigestIssueAdmin)
