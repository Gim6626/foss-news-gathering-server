from django.contrib import admin

from gatherer.models import *


class DigestRecordAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
    )
    list_display = (
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


admin.site.register(DigestRecord, DigestRecordAdmin)
admin.site.register(DigestRecordDuplicate, DigestRecordDuplicateAdmin)
admin.site.register(Project, ProjectAdmin)
