from django.contrib import admin

from gatherer.models import *


class DigestRecordAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
    )
    list_display = (
        'id',
        'dt',
        'title',
        'url',
    )


admin.site.register(DigestRecord, DigestRecordAdmin)
