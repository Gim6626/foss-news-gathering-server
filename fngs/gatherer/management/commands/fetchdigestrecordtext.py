import sys

from django.core.management.base import BaseCommand
from gatherer.models import *
import random
import os


from .logger import Logger
from .gatherfromsources import ParsingModuleFactory

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Command(BaseCommand):

    help = 'Fetch digest record text'

    def add_arguments(self, parser):
        parser.add_argument('-r',
                            '--use-random',
                            action='store_true',
                            help='Use random digest record ID')
        parser.add_argument('-s',
                            '--save-to-db',
                            action='store_true',
                            help='Save fetched text to database')
        parser.add_argument('-d',
                            '--digest-record-id',
                            help='Digest record ID')
        parser.add_argument('-o',
                            '--output-file',
                            help='File path to store fetched content')

    def handle(self, *args, **options):
        logger = Logger(os.path.join(SCRIPT_DIRECTORY, 'textsfetcher.log'))
        if options['use_random']:
            if options['digest_record_id']:
                logger.error('Specific digest record and random digest record are not compatible')
                sys.exit(1)
            sources_with_enabled_text_fetching = DigestRecordsSource.objects.filter(text_fetching_enabled=True)
            digest_record: DigestRecord = random.choice(DigestRecord.objects.filter(source__in=sources_with_enabled_text_fetching, text=None))
            logger.info(f'Randomly selected record #{digest_record.pk} "{digest_record.title}" {digest_record.url}')
        else:
            if not options['digest_record_id']:
                logger.error('"digest_record_id" option is required if random flag not used')
                sys.exit(1)
            digest_record_id = options['digest_record_id']
            digest_record: DigestRecord = DigestRecord.objects.get(pk=digest_record_id)
        logger.info(f'Fetching {digest_record.url}')
        text = fetch_digest_record_text(digest_record, logger)
        logger.info(f'Fetched {digest_record.url}')
        if options['save_to_db']:
            if options['output_file']:
                logger.error('Saving to DB and to file options are not compatible')
                sys.exit(1)
            digest_record.text = str(text)
            logger.info(f'Saving to database')
            digest_record.save()
            logger.info(f'Saved to database')
        else:
            if not options['output_file']:
                logger.error('"output_file" option is required if not saving to database')
                sys.exit(1)
            output_file_path = options['output_file']
            logger.info(f'Saving to {output_file_path}')
            fout = open(output_file_path, 'w')
            fout.write(str(text))
            logger.info(f'Saved to {output_file_path}')


def fetch_digest_record_text(digest_record: DigestRecord, logger):
    source: DigestRecordsSource = digest_record.source
    parsing_module = ParsingModuleFactory.create([source.name], logger)[0]
    return parsing_module.fetch_url(digest_record.url)
