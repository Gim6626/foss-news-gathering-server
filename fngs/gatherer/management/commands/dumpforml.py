from django.core.management.base import BaseCommand

from gatherer.models import *

import logging
import os
import json
import math
from pprint import pprint


from .logger import Logger
custom_logger = Logger()
parse_all = False
records_limit: int or None = None
similar_records_limit: int or None = None


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
        parser.add_argument('-a',
                            '--all',
                            action='store_true',
                            help='Export all, including not IN_DIGEST records')
        parser.add_argument('-s',
                            '--similar-records-save-path',
                            help='File path to store digest similar records')
        parser.add_argument('-r',
                            '--records-limit',
                            help='Dump only specified count of records')
        parser.add_argument('-p',
                            '--similar-records-limit',
                            help='Dump only specified count of similar records')
        parser.add_argument('DIGEST_RECORDS_SAVE_PATH',
                            help='File path to store digest records')

    def handle(self, *args, **options):
        self._init_globals(**options)
        digest_records_plain = []
        digest_record_object: DigestRecord
        custom_logger.info('Started preparation of digest records')
        if parse_all:
            digest_records_queryset = DigestRecord.objects.all()
        else:
            digest_records_queryset = DigestRecord.objects.filter(state='IN_DIGEST')
        last_printed_percent = None
        for digest_record_object_i, digest_record_object in enumerate(digest_records_queryset):
            if not parse_all and digest_record_object.digest_issue is None:
                custom_logger.error(f'Empty digest issue for digest record object #{digest_record_object.id}')
            digest_record_plain = {
                'id': digest_record_object.id,
                'datetime': (digest_record_object.dt if digest_record_object.dt else digest_record_object.gather_dt).strftime(DATETIME_FORMAT),
                'digest_number': digest_record_object.digest_issue.number if digest_record_object.digest_issue else None,
                'state': digest_record_object.state,
                'title': digest_record_object.title,
                'description': digest_record_object.cleared_description,
                'type': digest_record_object.content_type,
                'category': digest_record_object.content_category,
                'keywords': [{'name': k.name, 'foss': not k.proprietary, 'generic': k.is_generic}
                             for k in digest_record_object.title_keywords.all()] if digest_record_object.title_keywords else [],
                'language': digest_record_object.language,
                'url': digest_record_object.url,
            }
            digest_records_plain.append(digest_record_plain)
            percent = math.floor(digest_record_object_i / digest_records_queryset.count() * 100)
            if last_printed_percent is None or percent != last_printed_percent:
                custom_logger.info(f'Processed {percent}%')
                last_printed_percent = percent
            if records_limit is not None and digest_record_object_i > records_limit:
                custom_logger.info('Stopped export because of set records limit')
                break
        if last_printed_percent is not None and last_printed_percent != 100:
            custom_logger.info(f'Processed 100%')
        custom_logger.info('Finished preparation of digest records')

        digest_similar_records_plain = []
        if options['similar_records_save_path']:
            digest_similar_records_object: SimilarDigestRecords
            custom_logger.info('Started preparation of similar digest records')
            digest_similar_records_queryset = SimilarDigestRecords.objects.all()
            last_printed_percent = None
            for digest_similar_records_object_i, digest_similar_records_object in enumerate(digest_similar_records_queryset):
                if not parse_all and digest_similar_records_object.digest_issue is None:
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
                if similar_records_limit is not None and digest_similar_records_object_i > similar_records_limit:
                    custom_logger.info('Stopped export because of set similar records limit')
                    break
            if last_printed_percent is not None and last_printed_percent != 100:
                custom_logger.info(f'Processed 100%')
            custom_logger.info('Finished preparation of similar digest records')

        custom_logger.info(f'Saving digest records to "{options["DIGEST_RECORDS_SAVE_PATH"]}"')
        with open(options['DIGEST_RECORDS_SAVE_PATH'], 'w') as fout:
            json.dump(digest_records_plain, fout, indent=4)
        custom_logger.info('Saved')
        if options['similar_records_save_path']:
            custom_logger.info(f'Saving similar digest records to "{options["similar_records_save_path"]}"')
            with open(options['similar_records_save_path'], 'w') as fout:
                json.dump(digest_similar_records_plain, fout, indent=4)
            custom_logger.info('Saved')

    def _init_globals(self, **options):
        if options['debug']:
            custom_logger.console_handler.setLevel(logging.DEBUG)
        if options['all'] is not None:
            global parse_all
            parse_all = options['all']
        if options['records_limit'] is not None:
            global records_limit
            records_limit = int(options['records_limit'])
        if options['similar_records_limit'] is not None:
            global similar_records_limit
            similar_records_limit = int(options['similar_records_limit'])
