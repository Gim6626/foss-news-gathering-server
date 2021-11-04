from django.core.management.base import BaseCommand

from gatherer.models import *

import logging
import os
import json
import math
from pprint import pprint


from .logger import Logger
custom_logger = Logger()


SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Command(BaseCommand):
    help = 'Dump Digest Records data for Machine Learning tasks'

    def add_arguments(self, parser):
        # TODO: Option to list available sources
        parser.add_argument('-d',
                            '--debug',
                            action='store_true',
                            help='Debug mode')
        parser.add_argument('DIGEST_RECORDS_SAVE_PATH',
                            help='File path to store digest records')
        parser.add_argument('DIGEST_SIMILAR_RECORDS_SAVE_PATH',
                            help='File path to store digest similar records')

    def handle(self, *args, **options):
        self._init_globals(**options)
        digest_records_plain = []
        digest_record_object: DigestRecord
        custom_logger.info('Started preparation of digest records')
        digest_records_queryset = DigestRecord.objects.filter(state='IN_DIGEST')
        last_printed_percent = None
        for digest_record_object_i, digest_record_object in enumerate(digest_records_queryset):
            if digest_record_object.digest_issue is None:
                custom_logger.error(f'Empty digest issue for digest record object #{digest_record_object.id}')
            digest_record_plain = {
                'id': digest_record_object.id,
                'datetime': (digest_record_object.dt if digest_record_object.dt else digest_record_object.gather_dt).strftime(DATETIME_FORMAT),
                'digest_number': digest_record_object.digest_issue.number if digest_record_object.digest_issue else None,
                'title': digest_record_object.title,
                'description': digest_record_object.cleared_description,
                'type': digest_record_object.content_type,
                'category': digest_record_object.content_category,
                'keywords': [k.name for k in digest_record_object.title_keywords.all()] if digest_record_object.title_keywords else [],
                'language': digest_record_object.language,
                'url': digest_record_object.url,
            }
            digest_records_plain.append(digest_record_plain)
            percent = math.floor(digest_record_object_i / digest_records_queryset.count() * 100)
            if last_printed_percent is None or percent != last_printed_percent:
                custom_logger.info(f'Processed {percent}%')
                last_printed_percent = percent
            # break
        if last_printed_percent is not None and last_printed_percent != 100:
            custom_logger.info(f'Processed 100%')
        custom_logger.info('Finished preparation of digest records')
        # pprint(digest_records_plain)
        digest_similar_records_plain = []
        digest_similar_records_object: DigestRecordDuplicate
        custom_logger.info('Started preparation of similar digest records')
        digest_similar_records_queryset = DigestRecordDuplicate.objects.all()
        last_printed_percent = None
        for digest_similar_records_object_i, digest_similar_records_object in enumerate(digest_similar_records_queryset):
            if digest_similar_records_object.digest_issue is None:
                custom_logger.error(f'Empty digest issue for digest similar records object #{digest_similar_records_object.id}')
            digest_similar_records_one_plain = {
                'id': digest_similar_records_object.id,
                'digest_number': digest_record_object.digest_issue.number if digest_record_object.digest_issue else None,
                'digest_records_ids': [dr.id for dr in digest_similar_records_object.digest_records.all()],
            }
            digest_similar_records_plain.append(digest_similar_records_one_plain)
            percent = math.floor(digest_similar_records_object_i / digest_similar_records_queryset.count() * 100)
            if last_printed_percent is None or percent != last_printed_percent:
                custom_logger.info(f'Processed {percent}%')
                last_printed_percent = percent
            # break
        # pprint(digest_similar_records_plain)
        if last_printed_percent is not None and last_printed_percent != 100:
            custom_logger.info(f'Processed 100%')
        custom_logger.info('Finished preparation of similar digest records')

        custom_logger.info(f'Saving digest records to "{options["DIGEST_RECORDS_SAVE_PATH"]}"')
        with open(options['DIGEST_RECORDS_SAVE_PATH'], 'w') as fout:
            json.dump(digest_records_plain, fout, indent=4)
        custom_logger.info('Saved')
        custom_logger.info(f'Saving similar digest records to "{options["DIGEST_SIMILAR_RECORDS_SAVE_PATH"]}"')
        with open(options['DIGEST_SIMILAR_RECORDS_SAVE_PATH'], 'w') as fout:
            json.dump(digest_similar_records_plain, fout, indent=4)
        custom_logger.info('Saved')

    def _init_globals(self, **options):
        if options['debug']:
            custom_logger.console_handler.setLevel(logging.DEBUG)
