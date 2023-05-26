import logging
import pathlib
import sys
import time
import random
from enum import Enum

from django.core.management.base import BaseCommand

from gatherer.models import (
    DigestRecord,
    DigestRecordsSource,
)
from .gatherfromsources import ParsingModuleFactory

SCRIPT_DIRECTORY = pathlib.Path(__file__).parent.absolute()


class FetcherMode(Enum):
    ADHOC = 'adhoc'
    DAEMON = 'daemon'


DEFAULT_FETCHER_MODE = FetcherMode.ADHOC
DEFAULT_FETCHING_TIMEOUT_SECONDS = 60


class Command(BaseCommand):

    help = 'Fetch digest record text (in adhoc or daemon mode)'

    def add_arguments(self, parser):
        parser.add_argument('-r',
                            '--random',
                            action='store_true',
                            help='use random digest record ID')
        parser.add_argument('-s',
                            '--save-to-db',
                            action='store_true',
                            help='save fetched text to database')
        parser.add_argument('-t',
                            '--timeout',
                            type=int,
                            default=DEFAULT_FETCHING_TIMEOUT_SECONDS,
                            help='test fetching timeout in seconds for `daemon` mode')
        parser.add_argument('-c',
                            '--source',
                            help='source to select random digest record from')
        parser.add_argument('-d',
                            '--debug',
                            action='store_true',
                            help='debug mode')
        parser.add_argument('-i',
                            '--digest-record-id',
                            help='digest record ID')
        parser.add_argument('-o',
                            '--output-file',
                            help='file path to store fetched content')
        parser.add_argument('-m',
                            '--mode',
                            choices=[mode.value for mode in FetcherMode],
                            default=DEFAULT_FETCHER_MODE.value,
                            help=f'fetcher mode, default - `{DEFAULT_FETCHER_MODE.value}`')

    def handle(self, *args, **options):
        self._setup_logging(options)
        try:
            self._check_options(options)
            logging.info(f'Using `{options["mode"].value}` mode')
            match options['mode']:
                case FetcherMode.ADHOC:
                    self._fetch_one(options)
                case FetcherMode.DAEMON:
                    try:
                        while True:
                            self._fetch_one(options)
                            logging.info(f'Sleeping {options["timeout"]} second(s)')
                            time.sleep(options["timeout"])
                    except Exception as e:
                        logging.error(e)
                case _:
                    raise Exception(f'Invalid mode `{options["mode"]}`')
        except KeyboardInterrupt:
            logging.info('Interrupted')
        except Exception as e:
            logging.error(e)
            sys.exit(1)

    @staticmethod
    def _setup_logging(options):
        logging.basicConfig(level=logging.INFO if not options['debug'] else logging.DEBUG,
                            format='[%(asctime)s] %(levelname)s: %(message)s')

    @staticmethod
    def _check_options(options):
        options['mode'] = FetcherMode.ADHOC if options['mode'] == FetcherMode.ADHOC.value else FetcherMode.DAEMON
        if options['mode'] is FetcherMode.DAEMON:
            options_not_supported_for_daemon_mode = ('source', 'output_file', 'digest_record_id')
            for option_key in options_not_supported_for_daemon_mode:
                if options[option_key]:
                    raise Exception(f'`--{option_key.replace("_", "-")}` argument is not supported for daemon mode')
            options_required_for_daemon_mode = ('random', 'save_to_db')
            for option_key in options_required_for_daemon_mode:
                if not options[option_key]:
                    raise Exception(f'`--{option_key.replace("_", "-")}` argument is required for daemon mode')
        else:
            if options['timeout']:
                raise Exception('`--timeout` is supported only for `daemon` mode')
        if options['random'] and options['digest_record_id']:
            raise Exception('`--digest-record-id` and `--random` options are not compatible')
        if not options['random']:
            if options['digest_record_id'] is None:
                raise Exception('`--digest-record-id` option is required if random flag not set')
            if options['source']:
                raise Exception('`--source` option is incompatible with `--digest-record-id`')
            if options['save_to_db'] and options['output_file']:
                raise Exception('`--save-to-db` and `--output-file` options are not compatible')

    @staticmethod
    def _fetch_one(options):
        digest_record: DigestRecord
        if options['random']:
            sources_with_enabled_text_fetching = DigestRecordsSource.objects.filter(text_fetching_enabled=True)
            if options['source']:
                logging.info(f'Selected source - "{options["source"].name}"')
                selected_sources = DigestRecordsSource.objects.filter(name=options['source'])
                if not selected_sources:
                    raise Exception(f'Failed to find source with name "{options["source"]}"')
                selected_source = selected_sources[0]
                if selected_source not in sources_with_enabled_text_fetching:
                    raise Exception(f'Text fetching is not enabled for source with name "{options["source"]}", available are {[s.name for s in sources_with_enabled_text_fetching]}')  # noqa
                digest_records_without_text_from_selected_source = DigestRecord.objects.filter(source=selected_source, text=None)
                if not digest_records_without_text_from_selected_source:
                    logging.info(f'No digest records without text found in selected source "{options["source"].name}"')
                    return
                digest_record = random.choice(digest_records_without_text_from_selected_source)
            else:
                logging.info(f'{len(sources_with_enabled_text_fetching)} source(s) with enabled text fetching found')
                digest_records_without_text = DigestRecord.objects.filter(source__in=sources_with_enabled_text_fetching, text=None)
                logging.info(f'{len(digest_records_without_text)} digest records without text found')
                digest_record = random.choice(digest_records_without_text)
            logging.info(f'Randomly selected digest record - #{digest_record.pk} "{digest_record.title}"')
        else:
            digest_record = DigestRecord.objects.get(pk=options['digest_record_id'])
            logging.info(f'Taken digest record from option - #{digest_record.pk} "{digest_record.title}"')
        logging.info(f'Fetching text from URL {digest_record.url}')
        text = fetch_digest_record_text(digest_record)
        logging.info(f'Fetched text from URL {digest_record.url}')
        if options['save_to_db']:
            digest_record.text = str(text)
            logging.info(f'Saving to database')
            digest_record.save()
            logging.info(f'Saved to database')
        else:
            output_file_path = None
            if options['output_file'] is None:
                logging.info('"output_file" option is not set, using STDOUT')
                logging.info(f'Printing digest record text to STDOUT')
                fout = sys.stdout
            else:
                output_file_path = pathlib.Path(options['output_file']).absolute()
                logging.info(f'Saving digest record text to "{output_file_path}"')
                fout = open(output_file_path, 'w')
            fout.write(str(text))
            if options['output_file'] is None:
                logging.info(f'Printed digest record text to STDOUT')
            else:
                logging.info(f'Saved digest record text to "{output_file_path}"')
                fout.close()


def fetch_digest_record_text(digest_record: DigestRecord):
    source: DigestRecordsSource = digest_record.source
    parsing_module = ParsingModuleFactory.create([source.name], logging.getLogger())[0]
    return parsing_module.fetch_url(digest_record.url)
