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
    )


admin.site.register(DigestRecord, DigestRecordAdmin)
