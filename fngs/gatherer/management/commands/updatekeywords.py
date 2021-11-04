from django.core.management.base import BaseCommand

from gatherer.models import *

import logging
import os
import re
import math


from .logger import Logger
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
custom_logger = Logger(os.path.join('keywordsupdate.log'))
from .sources import BasicParsingModule


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

    def handle(self, *args, **options):
        self._init_globals(**options)
        custom_logger.info(f'Saving log to "{custom_logger.file_path}"')
        custom_logger.info('Started updating keywords in digest records')
        digest_records_queryset = DigestRecord.objects.all()
        last_printed_percent = None
        digest_record_object: DigestRecord
        keywords_queryset = Keyword.objects.all()
        updated_digest_records_count = 0
        for digest_record_object_i, digest_record_object in enumerate(digest_records_queryset):
            title_keywords_to_save = []
            for keyword in keywords_queryset:
                if BasicParsingModule.find_keyword_in_title(keyword.name, digest_record_object.title):
                    title_keywords_to_save.append(keyword)
            if set(title_keywords_to_save) != set(digest_record_object.title_keywords.all()):
                custom_logger.debug(f'Need to update keywords for digest record #{digest_record_object.id} "{digest_record_object.title}", old keywords were {sorted([k.name for k in digest_record_object.title_keywords.all()])}, new keywords are {sorted([k.name for k in title_keywords_to_save])}')
                digest_record_object.title_keywords.set(title_keywords_to_save)
                custom_logger.debug('Updated')
                updated_digest_records_count += 1
            percent = math.floor(digest_record_object_i / digest_records_queryset.count() * 100)
            if last_printed_percent is None or percent != last_printed_percent:
                custom_logger.info(f'Processed {percent}%')
                last_printed_percent = percent
        if last_printed_percent is not None and last_printed_percent != 100:
            custom_logger.info(f'Processed 100%')
        custom_logger.info(f'Finished updating keywords in digest records, updated {updated_digest_records_count}/{digest_records_queryset.count()} ({math.floor(updated_digest_records_count / digest_records_queryset.count() * 100)}) digest records')

    def _init_globals(self, **options):
        if options['debug']:
            custom_logger.console_handler.setLevel(logging.DEBUG)
