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
keywords = {}


class Command(BaseCommand):
    help = 'Parse FOSS internet sources and save to database'

    def add_arguments(self, parser):
        # TODO: Option to list available sources
        parser.add_argument('MODULE',
                            type=str,
                            help='Parsing module')
        parser.add_argument('DAYS_COUNT',
                            type=int,
                            help='Days to gather')

    def handle(self, *args, **options):
        self._init_globals(**options)
        parsing_modules = ParsingModuleFactory.create(parsing_modules_names)
        posts_data_from_multiple_sources = self._parse(parsing_modules)
        self._save_to_database(posts_data_from_multiple_sources)

    def _parse(self, parsing_modules):
        posts_data_from_multiple_sources: List[PostsData] = []
        logger.info('Started parsing all sources')
        for parsing_module in parsing_modules:
            logger.info(f'Started parsing {parsing_module.source_name}')
            posts_data = parsing_module.parse(days_count)
            posts_data_one = PostsData(parsing_module.source_name,
                                       posts_data,
                                       parsing_module.warning)
            for post_data in posts_data_one.posts_data_list:
                logger.info(f'New post {post_data.dt if post_data.dt is not None else "?"} "{post_data.title}" {post_data.url}')
            logger.debug(f'Parsed from {parsing_module.source_name}: {[(post_data.title, post_data.url) for post_data in posts_data_one.posts_data_list]}')
            posts_data_from_multiple_sources.append(posts_data_one)
            logger.info(f'Finished parsing {parsing_module.source_name}, got {len(posts_data_one.posts_data_list)} post(s)')
        logger.info(f'Finished parsing all sources, got {sum((len(posts_data_one.posts_data_list) for posts_data_one in posts_data_from_multiple_sources))} digest record(s) from {len(posts_data_from_multiple_sources)} source(s)')
        return posts_data_from_multiple_sources

    def _save_to_database(self, posts_data_from_multiple_sources):
        logger.info('Saving to database')
        added_digest_records_count = 0
        already_existing_digest_records_count = 0
        for posts_data in posts_data_from_multiple_sources:
            for post_data in posts_data.posts_data_list:
                short_post_data_str = f'{post_data.dt} "{post_data.title}" ({post_data.url})'
                similar_urls = DigestRecord.objects.filter(url=post_data.url)
                if similar_urls:
                    logger.warning(f'{short_post_data_str} ignored, found same in database')
                    already_existing_digest_records_count += 1
                    continue
                else:
                    logger.debug(f'Adding {short_post_data_str} to database')
                    digest_record = DigestRecord(dt=post_data.dt,
                                                 gather_dt=datetime.datetime.now(tz=dateutil.tz.tzlocal()),
                                                 title=post_data.title.strip(),
                                                 url=post_data.url,
                                                 state=DigestRecordState.UNKNOWN.name,
                                                 keywords=';'.join(post_data.keywords))
                    digest_record.save()
                    digest_record.projects.set(post_data.projects)
                    digest_record.save()
                    added_digest_records_count += 1
                    logger.debug(f'Added {short_post_data_str} to database')
        logger.info(f'Finished saving to database, added {added_digest_records_count} digest record(s), {already_existing_digest_records_count} already existed')

    def _init_globals(self, **options):
        init_logger()
        global days_count
        days_count = options['DAYS_COUNT']
        global parsing_modules_names
        if options['MODULE'] == 'ALL':
            parsing_modules_names = [ParsingModuleType(m) for m in PARSING_MODULES_TYPES]
        else:
            for m in options['MODULE'].split(','):
                if m not in PARSING_MODULES_TYPES:
                    logger.error(f'Invalid parsing module type "{m}", available are: {PARSING_MODULES_TYPES}')
                    sys.exit(2)
            parsing_modules_names = [ParsingModuleType(m) for m in options['MODULE'].split(',')]
        global keywords
        with open(os.path.join(SCRIPT_DIRECTORY, 'keywords.yaml'), 'r') as fin:
            keywords = yaml.safe_load(fin)


def init_logger():
    global logger



class ParsingModuleFactory:

    @staticmethod
    def create(parsing_module_types: List['ParsingModuleType']) -> List[BasicParsingModule]:
        return [ParsingModuleFactory.create_one(parsing_module_type) for parsing_module_type in parsing_module_types]

    @staticmethod
    def create_one(parsing_module_type: 'ParsingModuleType') -> BasicParsingModule:
        parsing_module_constructor = globals()[parsing_module_type.value + 'ParsingModule']
        parsing_module = parsing_module_constructor()
        return parsing_module


class ParsingModuleType(Enum):
    OPENNET_RU = OpenNetRuParsingModule.source_name
    LINUX_COM = LinuxComParsingModule.source_name
    OPENSOURCE_COM = OpenSourceComParsingModule.source_name
    ITSFOSS_COM = ItsFossComParsingModule.source_name
    LINUXORG_RU = LinuxOrgRuParsingModule.source_name
    ANALYTICSINDIAMAG_COM = AnalyticsIndiaMagComParsingModule.source_name
    ARSTECHNICA_COM = ArsTechnicaComParsingModule.source_name
    HACKADAY_COM = HackadayComParsingModule.source_name
    JAXENTER_COM = JaxenterComParsingModule.source_name
    LINUXINSIDER_COM = LinuxInsiderComParsingModule.source_name
    MASHABLE_COM = MashableComParsingModule.source_name
    SDTIMES_COM = SdTimesComParsingModule.source_name
    SECURITYBOULEVARD_COM = SecurityBoulevardComParsingModule.source_name
    SILICONANGLE_COM = SiliconAngleComParsingModule.source_name
    TECHCRUNCH_COM = TechCrunchComParsingModule.source_name
    TECHNODE_COM = TechNodeComParsingModule.source_name
    THENEXTWEB_COM = TheNextWebComParsingModule.source_name
    VENTUREBEAT_COM = VentureBeatComParsingModule.source_name
    THREEDPRINTINGMEDIA_NETWORK = ThreeDPrintingMediaNetworkParsingModule.source_name
    CBRONLINE_COM = CbrOnlineComParsingModule.source_name
    HELPNETSECURITY_COM = HelpNetSecurityComParsingModule.source_name
    SECURITYSALES_COM = SecuritySalesComParsingModule.source_name
    TECHRADAR_COM = TechRadarComParsingModule.source_name
    TFIR_IO = TfirIoParsingModule.source_name
    ZDNET_COM_LINUX = ZdNetComLinuxParsingModule.source_name
    LINUXFOUNDATION_ORG = LinuxFoundationOrgParsingModule.source_name
    HABR_COM_NEWS = HabrComNewsParsingModule.source_name
    HABR_COM_OPENSOURCE = HabrComOpenSourceParsingModule.source_name
    HABR_COM_LINUX = HabrComLinuxParsingModule.source_name
    HABR_COM_LINUX_DEV = HabrComLinuxDevParsingModule.source_name
    HABR_COM_NIX = HabrComNixParsingModule.source_name
    HABR_COM_DEVOPS = HabrComDevOpsParsingModule.source_name
    HABR_COM_SYS_ADM = HabrComSysAdmParsingModule.source_name
    HABR_COM_GIT = HabrComGitParsingModule.source_name
    YOUTUBE_COM_ALEKSEY_SAMOILOV = YouTubeComAlekseySamoilovParsingModule.source_name
    LOSST_RU = LosstRuParsingModule.source_name
    PINGVINUS_RU = PingvinusRuParsingModule.source_name
    ASTRALINUX_RU = AstraLinuxRuParsingModule.source_name
    BASEALT_RU = BaseAltRuParsingModule.source_name


PARSING_MODULES_TYPES = tuple((t.value for t in ParsingModuleType))
