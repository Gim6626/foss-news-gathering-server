from django.core.management.base import BaseCommand

from ds.models import *

import dateutil.parser
import logging
import sys
import os
import traceback
import lemminflect
import nltk
from bs4 import BeautifulSoup


from .sources import *

from .logger import Logger
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
custom_logger = Logger(os.path.join(SCRIPT_DIRECTORY, 'gatherfromsources.log'))

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

parsing_modules_names = []
days_count = None


class Command(BaseCommand):
    help = 'Parse FOSS internet sources and save to database'

    def add_arguments(self, parser):
        # TODO: Option to list available sources
        parser.add_argument('-d',
                            '--debug',
                            action='store_true',
                            help='Debug mode')
        parser.add_argument('MODULE',
                            type=str,
                            help='Parsing module')
        parser.add_argument('DAYS_COUNT',
                            type=int,
                            help='Days to gather')

    def handle(self, *args, **options):
        try:
            self._init_globals(**options)
            custom_logger.info(f'Saving log to "{custom_logger.file_path}"')
            parsing_modules = ParsingModuleFactory.create(parsing_modules_names, custom_logger)
            custom_logger.info('Started parsing all sources')
            for parsing_module in parsing_modules:
                parsing_result = self._parse(parsing_module)
                if parsing_result is not None:
                    iteration, posts_data_one = parsing_result
                    self._save_to_database(iteration, posts_data_one)
            custom_logger.info(f'Finished parsing all sources, all saved to database')  # TODO: Add stats
        except Exception as e:
            custom_logger.critical(e)
            custom_logger.critical(traceback.format_exc())
            sys.exit(1)

    def _parse(self, parsing_module):
        custom_logger.info(f'Started parsing {parsing_module.source_name}')
        parsing_result = parsing_module.parse(days_count)
        source = DigestRecordsSource.objects.get(name=parsing_module.source_name)
        datetime_now = datetime.datetime.now(tz=dateutil.tz.tzlocal())
        if parsing_result.success:
            posts_data_one = PostsData(parsing_module.source_name,
                                       parsing_module.projects,
                                       parsing_result.posts_data_after_filtration,
                                       parsing_module.language,
                                       parsing_module.filters,
                                       parsing_module.warning)
            iteration = DigestGatheringIteration(dt=datetime_now,
                                                 overall_count=parsing_result.overall_count,
                                                 source_enabled=True,
                                                 gathered_count=len(parsing_result.posts_data_after_filtration),
                                                 saved_count=0,
                                                 source=source)
            iteration.save()
            for post_data in posts_data_one.posts_data_list:
                custom_logger.info(f'New post {post_data.dt if post_data.dt is not None else "?"} "{post_data.title}" {post_data.url}')
            custom_logger.debug(f'Parsed from {parsing_module.source_name}: {[(post_data.title, post_data.url) for post_data in posts_data_one.posts_data_list]}')
            custom_logger.info(f'Finished parsing {parsing_module.source_name}, got {len(posts_data_one.posts_data_list)} post(s)')
            return iteration, posts_data_one
        elif not parsing_result.source_enabled:
            iteration = DigestGatheringIteration(dt=datetime_now,
                                                 overall_count=parsing_result.overall_count,
                                                 source_enabled=False,
                                                 gathered_count=0,
                                                 saved_count=0,
                                                 source=source)
            iteration.save()
            return None
        else:
            iteration = DigestGatheringIteration(dt=datetime_now,
                                                 source_enabled=True,
                                                 overall_count=parsing_result.overall_count,
                                                 gathered_count=len(parsing_result.posts_data_after_filtration),
                                                 saved_count=0,
                                                 source=source,
                                                 source_error=parsing_result.source_error,
                                                 parser_error=parsing_result.parser_error)
            iteration.save()
            return None

    def _save_to_database(self, iteration: DigestGatheringIteration, posts_data_one: PostsData):
        custom_logger.info(f'Saving to database for source "{posts_data_one.source_name}"')
        source = DigestRecordsSource.objects.get(name=posts_data_one.source_name)
        added_digest_records_count = 0
        already_existing_digest_records_count = 0
        already_existing_digest_records_dt_updated_count = 0
        for post_data in posts_data_one.posts_data_list:
            short_post_data_str = f'{post_data.dt} "{post_data.title}" ({post_data.url})'
            similar_records = DigestRecord.objects.filter(url=post_data.url)  # TODO: Replace check for similar records before and with "get"
            if similar_records:
                if not similar_records[0].dt:
                    similar_records[0].dt = post_data.dt
                    custom_logger.debug(f'{short_post_data_str} already exists in database, but without date, fix it')
                    already_existing_digest_records_dt_updated_count += 1
                    similar_records[0].save()
                else:
                    custom_logger.warning(f'{short_post_data_str} ignored, found same in database')
                    already_existing_digest_records_count += 1
                continue
            else:
                custom_logger.debug(f'Adding {short_post_data_str} to database')
                all_matched_keywords = []
                if post_data.filtered:
                    state = DigestRecordState.FILTERED.name
                else:
                    state = DigestRecordState.UNKNOWN.name
                for keyword_name in post_data.keywords:
                    matched_keywords_for_one = Keyword.objects.filter(name=keyword_name)
                    if len(matched_keywords_for_one) == 0:
                        custom_logger.error(f'Failed to find keywords with name "{keyword_name}" in database')
                    else:
                        if len(matched_keywords_for_one) > 1:
                            custom_logger.warning(f'More than one keyword with name "{keyword_name}" found in database')
                        all_matched_keywords += matched_keywords_for_one
                if state == DigestRecordState.UNKNOWN.name and all_matched_keywords:
                    enabled_and_valuable_matched_keywords = []
                    if not posts_data_one.filters:
                        for keyword in all_matched_keywords:
                            if keyword.enabled:
                                enabled_and_valuable_matched_keywords.append(keyword)
                        should_be_skipped = False
                    elif FiltrationType.SPECIFIC in posts_data_one.filters \
                            and FiltrationType.GENERIC in posts_data_one.filters:
                        should_be_skipped = True
                        for keyword in all_matched_keywords:
                            if keyword.enabled:
                                enabled_and_valuable_matched_keywords.append(keyword)
                    elif FiltrationType.SPECIFIC in posts_data_one.filters:
                        should_be_skipped = True
                        for keyword in all_matched_keywords:
                            if keyword.enabled and not keyword.is_generic:
                                enabled_and_valuable_matched_keywords.append(keyword)
                    else:
                        should_be_skipped = True
                        for keyword in all_matched_keywords:
                            if keyword.enabled and keyword.is_generic:
                                enabled_and_valuable_matched_keywords.append(keyword)
                    if enabled_and_valuable_matched_keywords:
                        should_be_skipped = False
                    if should_be_skipped:
                        custom_logger.warning(f'Record "{post_data.title}" ({post_data.url}) marked as skipped after keywords check')
                        state = DigestRecordState.SKIPPED.name
                    else:
                        all_proprietary = True
                        for keyword in enabled_and_valuable_matched_keywords:
                            if not keyword.proprietary:
                                all_proprietary = False
                                break
                        if all_proprietary and enabled_and_valuable_matched_keywords:
                            custom_logger.warning(f'Record "{post_data.title}" ({post_data.url}) marked as skipped because all it\'s enabled and valuable keywords {[k.name for k in enabled_and_valuable_matched_keywords]} are proprietary')
                            state = DigestRecordState.SKIPPED.name
                description = post_data.brief
                cleared_description = BeautifulSoup(description, 'lxml').text if description else None
                digest_record = DigestRecord(dt=post_data.dt,
                                             source=source,
                                             gather_dt=datetime.datetime.now(tz=dateutil.tz.tzlocal()),
                                             title=post_data.title.strip(),
                                             url=post_data.url,
                                             state=state,
                                             language=source.language,
                                             description=description,
                                             cleared_description=cleared_description)
                digest_record.save()
                digest_record.projects.set(source.projects.all())
                if all_matched_keywords:
                    digest_record.title_keywords.set(all_matched_keywords)
                digest_record.save()
                if digest_record.language == Language.ENGLISH.name:
                    if cleared_description:
                        self._save_lemmas(digest_record, cleared_description)
                    else:
                        custom_logger.debug(f'Skipped parsing lemmas for "{digest_record.title}" because cleared description is empty')
                else:
                    custom_logger.debug(f'Skipped parsing lemmas for "{digest_record.title}" because it is not english')
                added_digest_records_count += 1
                custom_logger.debug(f'Added {short_post_data_str} to database')
        iteration.saved_count = added_digest_records_count
        iteration.save()
        custom_logger.info(f'Finished saving to database for source "{posts_data_one.source_name}", added {added_digest_records_count} digest record(s), {already_existing_digest_records_count} already existed, dates filled for {already_existing_digest_records_dt_updated_count} existing record(s)')

    def _save_lemmas(self, digest_record, cleared_description):
        words = nltk.word_tokenize(cleared_description)
        word_lemmas_counts = {}
        for word in words:
            word_lemmas = lemminflect.getAllLemmas(word)
            lemmas_keys = ('NOUN', 'VERB', 'AUX', 'ADV', 'ADJ')
            word_lemmas_plain = []
            for lk in lemmas_keys:
                if lk in word_lemmas:
                    word_lemmas_plain += (l.lower() for l in word_lemmas[lk])
            if not word_lemmas and re.match(r'\w', word):
                word_lemmas_plain.append(word.lower())
            for l in word_lemmas_plain:
                if l not in word_lemmas_counts:
                    word_lemmas_counts[l] = 1
                else:
                    word_lemmas_counts[l] += 1
        for lemma_text, lemma_count_in_dr in word_lemmas_counts.items():
            existing_lemmas = Lemma.objects.filter(text=lemma_text)
            if not existing_lemmas:
                lemma_object = Lemma(text=lemma_text)
                lemma_object.save()
            else:
                lemma_object = existing_lemmas[0]
            existing_digest_record_lemmas = DigestRecordLemma.objects.filter(lemma=lemma_object,
                                                                             digest_record=digest_record)
            if not existing_digest_record_lemmas:
                digest_record_lemma = DigestRecordLemma(lemma=lemma_object,
                                                        digest_record=digest_record,
                                                        count=lemma_count_in_dr)
                digest_record_lemma.save()

    def _init_globals(self, **options):
        if options['debug']:
            custom_logger.console_handler.setLevel(logging.DEBUG)
        global days_count
        days_count = options['DAYS_COUNT']
        module = options['MODULE']
        global parsing_modules_names
        projects = Project.objects.values_list('name', flat=True)
        if module == 'ALL':
            sources_selected_by_user = DigestRecordsSource.objects.all()
        elif module in projects:
            sources_selected_by_user = DigestRecordsSource.objects.filter(projects__name__in=(module,))
        else:
            sources_names_selected_by_user = module.split(',')
            sources_selected_by_user = [source for source in DigestRecordsSource.objects.all() if source.name in sources_names_selected_by_user]
        if not sources_selected_by_user:
            custom_logger.error(f'Failed to find parsing modules matched "{module}"')
            sys.exit(1)
        enabled_sources_selected_by_user = []
        for source in sources_selected_by_user:
            if source.enabled:
                enabled_sources_selected_by_user.append(source)
            else:
                custom_logger.warning(f'Source "{source.name}" is disabled, not parsing')
        parsing_modules_names = [s.name for s in enabled_sources_selected_by_user]


class ParsingModuleFactory:

    @staticmethod
    def create(parsing_module_names: List[str], logger) -> List[BasicParsingModule]:
        return [ParsingModuleFactory.create_one(parsing_module_name, logger) for parsing_module_name in parsing_module_names]

    @staticmethod
    def create_one(parsing_module_name: str, logger) -> BasicParsingModule:
        parsing_module_constructor = globals()[parsing_module_name + 'ParsingModule']
        parsing_module = parsing_module_constructor(logger)
        return parsing_module
