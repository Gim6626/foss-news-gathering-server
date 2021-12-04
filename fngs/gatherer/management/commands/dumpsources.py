from typing import (
    List,
    Dict,
)
import json

from django.core.management.base import BaseCommand

from gatherer.models import *


class Command(BaseCommand):
    help = 'Dump Digest Records sources'

    def add_arguments(self, parser):
        parser.add_argument('OUTPUT_FILE_PATH',
                            help='File path to store sources')

    def handle(self, *args, **options):
        source_obj: DigestRecordsSource
        sources_plain: List[Dict] = []
        for source_obj in DigestRecordsSource.objects.all():
            source_records_good_count = DigestRecord.objects.filter(source=source_obj, state='IN_DIGEST').count()
            source_records_bad_count = DigestRecord.objects.filter(source=source_obj).exclude(state='IN_DIGEST').count()
            if source_records_good_count or source_records_bad_count:
                source_plain = {
                    'name': source_obj.name,
                    'data_url': source_obj.data_url,
                    'good_records_count': source_records_good_count,
                    'bad_records_count': source_records_bad_count,
                }
                sources_plain.append(source_plain)
        sources_plain_str = json.dumps(sources_plain, indent=4)
        fout = open(options['OUTPUT_FILE_PATH'], 'w')
        fout.write(sources_plain_str)
