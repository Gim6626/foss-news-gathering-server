from django.core.management.base import BaseCommand

from gatherer.models import *
import datetime
from enum import Enum
from typing import List
import dateutil.parser
import logging
import sys
import os
import yaml


from .sources import *
from .logger import logger


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
        self._init_globals(**options)
        parsing_modules = ParsingModuleFactory.create(parsing_modules_names)
        logger.info('Started parsing all sources')
        for parsing_module in parsing_modules:
            parsing_result = self._parse(parsing_module)
            if parsing_result is not None:
                iteration, posts_data_one = parsing_result
                self._save_to_database(iteration, posts_data_one)
        logger.info(f'Finished parsing all sources, all saved to database')  # TODO: Add stats

    def _parse(self, parsing_module):
        logger.info(f'Started parsing {parsing_module.source_name}')
        parsing_result = parsing_module.parse(days_count)
        source = DigestRecordsSource.objects.get(name=parsing_module.source_name)
        datetime_now = datetime.datetime.now(tz=dateutil.tz.tzlocal())
        if parsing_result.success:
            posts_data_one = PostsData(parsing_module.source_name,
                                       parsing_module.projects,
                                       parsing_result.posts_data_after_filtration,
                                       parsing_module.language,
                                       parsing_module.warning)
            iteration = DigestGatheringIteration(dt=datetime_now,
                                                 overall_count=parsing_result.overall_count,
                                                 source_enabled=True,
                                                 gathered_count=len(parsing_result.posts_data_after_filtration),
                                                 saved_count=0,
                                                 source=source)
            iteration.save()
            for post_data in posts_data_one.posts_data_list:
                logger.info(f'New post {post_data.dt if post_data.dt is not None else "?"} "{post_data.title}" {post_data.url}')
            logger.debug(f'Parsed from {parsing_module.source_name}: {[(post_data.title, post_data.url) for post_data in posts_data_one.posts_data_list]}')
            logger.info(f'Finished parsing {parsing_module.source_name}, got {len(posts_data_one.posts_data_list)} post(s)')
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
        logger.info(f'Saving to database for source "{posts_data_one.source_name}"')
        source = DigestRecordsSource.objects.get(name=posts_data_one.source_name)
        added_digest_records_count = 0
        already_existing_digest_records_count = 0
        already_existing_digest_records_dt_updated_count = 0
        for post_data in posts_data_one.posts_data_list:
            short_post_data_str = f'{post_data.dt} "{post_data.title}" ({post_data.url})'
            similar_records = DigestRecord.objects.filter(url=post_data.url)  # TODO: Replace check for duplicates before and with "get"
            if similar_records:
                if not similar_records[0].dt:
                    similar_records[0].dt = post_data.dt
                    logger.debug(f'{short_post_data_str} already exists in database, but without date, fix it')
                    already_existing_digest_records_dt_updated_count += 1
                    similar_records[0].save()
                else:
                    logger.warning(f'{short_post_data_str} ignored, found same in database')
                    already_existing_digest_records_count += 1
                continue
            else:
                logger.debug(f'Adding {short_post_data_str} to database')
                all_matched_keywords = []
                for keyword_name in post_data.keywords:
                    matched_keywords_for_one = Keyword.objects.filter(name=keyword_name)
                    if len(matched_keywords_for_one) == 0:
                        logger.error(f'Failed to find keywords with name "{keyword_name}" in database')
                    elif len(matched_keywords_for_one) > 1:
                        logger.error(f'More than one keyword with name "{keyword_name}" in database')
                    else:
                        all_matched_keywords.append(matched_keywords_for_one[0])
                digest_record = DigestRecord(dt=post_data.dt,
                                             source=source,
                                             gather_dt=datetime.datetime.now(tz=dateutil.tz.tzlocal()),
                                             title=post_data.title.strip(),
                                             url=post_data.url,
                                             state=DigestRecordState.UNKNOWN.name
                                                   if not post_data.filtered
                                                   else DigestRecordState.FILTERED.name,
                                             language=source.language,
                                             description=post_data.brief)
                digest_record.save()
                digest_record.projects.set(source.projects.all())
                if all_matched_keywords:
                    digest_record.title_keywords.set(all_matched_keywords)
                digest_record.save()
                added_digest_records_count += 1
                logger.debug(f'Added {short_post_data_str} to database')
        iteration.saved_count = added_digest_records_count
        iteration.save()
        logger.info(f'Finished saving to database for source "{posts_data_one.source_name}", added {added_digest_records_count} digest record(s), {already_existing_digest_records_count} already existed, dates filled for {already_existing_digest_records_dt_updated_count} existing record(s)')

    def _init_globals(self, **options):
        if options['debug']:
            logger.console_handler.setLevel(logging.DEBUG)
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
        enabled_sources_selected_by_user = []
        for source in sources_selected_by_user:
            if source.enabled:
                enabled_sources_selected_by_user.append(source)
            else:
                logger.warning(f'Source "{source.name}" is disabled, not parsing')
        parsing_modules_names = [s.name for s in enabled_sources_selected_by_user]


class ParsingModuleFactory:

    @staticmethod
    def create(parsing_module_names: List[str]) -> List[BasicParsingModule]:
        return [ParsingModuleFactory.create_one(parsing_module_name) for parsing_module_name in parsing_module_names]

    @staticmethod
    def create_one(parsing_module_name: str) -> BasicParsingModule:
        parsing_module_constructor = globals()[parsing_module_name + 'ParsingModule']
        parsing_module = parsing_module_constructor()
        return parsing_module
