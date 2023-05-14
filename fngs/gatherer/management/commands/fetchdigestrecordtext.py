import pathlib
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
        parser.add_argument('-c',
                            '--source',
                            help='Source to select random digest record from')
        parser.add_argument('-d',
                            '--digest-record-id',
                            help='Digest record ID')
        parser.add_argument('-o',
                            '--output-file',
                            help='File path to store fetched content')

    def handle(self, *args, **options):
        logger = Logger(os.path.join(SCRIPT_DIRECTORY, 'textsfetcher.log'))
        try:
            if options['use_random']:
                if options['digest_record_id']:
                    raise Exception('Specific digest record and random digest record are not compatible')
                sources_with_enabled_text_fetching = DigestRecordsSource.objects.filter(text_fetching_enabled=True)
                if options['source']:
                    selected_sources = DigestRecordsSource.objects.filter(name=options['source'])
                    if not selected_sources:
                        raise Exception(f'Failed to find source with name "{options["source"]}"')
                    selected_source = selected_sources[0]
                    if selected_source not in sources_with_enabled_text_fetching:
                        raise Exception(f'Text fetching is not enabled for source with name "{options["source"]}", available are {[s.name for s in sources_with_enabled_text_fetching]}')
                else:
                    selected_source = random.choice(sources_with_enabled_text_fetching)
                digest_record: DigestRecord = random.choice(DigestRecord.objects.filter(source=selected_source, text=None))
                logger.info(f'Randomly selected record #{digest_record.pk} "{digest_record.title}" {digest_record.url}')
            else:
                if options['digest_record_id'] is None:
                    raise Exception('`--digest-record-id` option is required if random flag not used')
                if options['source']:
                    raise Exception('`--source` option is incompatible with `--digest-record-id`')
                digest_record_id = options['digest_record_id']
                digest_record: DigestRecord = DigestRecord.objects.get(pk=digest_record_id)
            logger.info(f'Fetching {digest_record.url}')
            text = fetch_digest_record_text(digest_record, logger)
            logger.info(f'Fetched {digest_record.url}')
            if options['save_to_db']:
                if options['output_file']:
                    raise Exception('Saving to DB and to file options are not compatible')
                digest_record.text = str(text)
                logger.info(f'Saving to database')
                digest_record.save()
                logger.info(f'Saved to database')
            else:
                if options['output_file'] is None:
                    logger.info('"output_file" option is not set, using STDOUT')
                    logger.info(f'Printing digest record text to STDOUT')
                    fout = sys.stdout
                else:
                    output_file_path = pathlib.Path(options['output_file']).absolute()
                    logger.info(f'Saving digest record text to "{output_file_path}"')
                    fout = open(output_file_path, 'w')
                fout.write(str(text))
                if options['output_file'] is None:
                    logger.info(f'Printed digest record text to STDOUT')
                else:
                    logger.info(f'Saved digest record text to "{output_file_path}"')
                    fout.close()
        except Exception as e:
            logger.error(e)


def fetch_digest_record_text(digest_record: DigestRecord, logger):
    source: DigestRecordsSource = digest_record.source
    parsing_module = ParsingModuleFactory.create([source.name], logger)[0]
    return parsing_module.fetch_url(digest_record.url)
