from django.contrib import admin

from ds.models import *
from common.urlsbuilder import object_modification_url


class LemmaAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id',
    )
    list_display = (
        'id',
        'text',
    )
    search_fields = (
        'text',
    )


class DigestRecordLemmaAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
    )
    list_display = (
        'id',
        'link_to_lemma',
        'link_to_digest_record',
        'count',
    )

    autocomplete_fields = (
        'digest_record',
    )

    def link_to_lemma(self, obj):
        return object_modification_url('ds', 'lemma', obj.lemma.id if obj.lemma else None, obj.lemma.text)

    def link_to_digest_record(self, obj):
        return object_modification_url('gatherer', 'digestrecord', obj.digest_record.id if obj.digest_record else None, str(obj.digest_record))


admin.site.register(Lemma, LemmaAdmin)
admin.site.register(DigestRecordLemma, DigestRecordLemmaAdmin)
