from django.core.management.base import BaseCommand
from gatherer.models import (
    DigestRecord,
    DigestRecordState,
)
from abc import ABCMeta, abstractmethod
import datetime
from enum import Enum
from typing import List
import xml.etree.ElementTree as ET
import dateutil.parser
from lxml import html
import logging
import sys
import requests
import re
import os
import traceback
import yaml
from pprint import pprint


SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

logger: logging.Logger = None
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
            posts_data = parsing_module.parse()
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
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.WARNING)

    logging_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

    # TODO: Replace with TimedRotatingFileHandler
    file_handler = logging.FileHandler(os.path.join(SCRIPT_DIRECTORY,
                                                    'gatherfromsources.log'))
    file_handler.setFormatter(logging_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)


def shorten_text(s: str, max_length: int = 20):
    if s is None:
        return None
    elif len(s) < max_length:
        return s
    else:
        return s[:max_length - 3] + '...'


class PostData:

    def __init__(self,
                 dt: datetime.datetime,
                 title: str,
                 url: str,
                 brief: str):
        self.dt = dt
        self.title = title
        self.url = url
        self.brief = brief
        self.keywords = []

    def __str__(self):
        return f'{self.dt} -- {self.url} -- {self.title} -- {shorten_text(self.brief)}'


class PostsData:

    def __init__(self,
                 source_name: str,
                 posts_data_list: List[PostData],
                 warning: str = None):
        self.source_name = source_name
        self.posts_data_list = posts_data_list
        self.warning = warning


class FiltrationType(Enum):
    GENERIC = 'generic'
    SPECIFIC = 'specific'


class BasicParsingModule(metaclass=ABCMeta):

    source_name = None
    warning = None
    filtration_needed = False
    filters = []

    def parse(self) -> List[PostData]:
        try:
            posts_data: List[PostData] = self._parse()
        except Exception as e:
            logger.error(f'Failed to parse "{self.source_name}" source: {str(e)}')
            logger.error(traceback.format_exc())
            return []
        try:
            filtered_posts_data: List[PostData] = self._filter_out(posts_data)
            return filtered_posts_data
        except Exception as e:
            logger.error(f'Failed to filter data parsed from "{self.source_name}" source: {str(e)}')
            logger.error(traceback.format_exc())
            return []

    @abstractmethod
    def _parse(self) -> List[PostData]:
        pass

    def _filter_out(self, posts_data: List[PostData]):
        filtered_posts_data: List[PostData] = posts_data
        filtered_posts_data = self._filter_out_old(filtered_posts_data)
        filtered_posts_data = self._filter_out_by_keywords(filtered_posts_data)
        return filtered_posts_data

    def _filter_out_by_keywords(self, posts_data: List[PostData]):
        if not self.filtration_needed:
            return posts_data
        filtered_posts_data: List[PostData] = []
        keywords_to_check = []
        if FiltrationType.GENERIC in self.filters:
            keywords_to_check += keywords['generic']
        if FiltrationType.SPECIFIC in self.filters:
            keywords_to_check += keywords['specific']
        for post_data in posts_data:
            matched = False
            for keyword in keywords_to_check:
                if keyword in post_data.keywords:
                    continue
                if re.search(rf'\b{re.escape(keyword)}\b', post_data.title, re.IGNORECASE):
                    matched = True
                    post_data.keywords.append(keyword)
            if matched:
                logger.debug(f'"{post_data.title}" from "{self.source_name}" added because it contains keywords {post_data.keywords}')
                filtered_posts_data.append(post_data)
            else:
                logger.warning(f'"{post_data.title}" ({post_data.url}) from "{self.source_name}" filtered out cause not contains none of expected keywords')
        return filtered_posts_data

    def _filter_out_old(self, posts_data: List[PostData]) -> List[PostData]:
        filtered_posts_data: List[PostData] = []
        dt_now = datetime.datetime.now(tz=dateutil.tz.tzlocal())
        for post_data in posts_data:
            if post_data.dt is not None and (dt_now - post_data.dt).days > days_count:
                logger.debug(f'"{post_data.title}" from "{self.source_name}" filtered as too old ({post_data.dt})')
            else:
                filtered_posts_data.append(post_data)
        return filtered_posts_data


class RssBasicParsingModule(BasicParsingModule):

    rss_url = None
    item_tag_name = None
    title_tag_name = None
    pubdate_tag_name = None
    link_tag_name = None
    description_tag_name = None

    def __init__(self):
        self.rss_data_root = None

    def _parse(self):
        posts_data: List[PostData] = []
        response = requests.get(self.rss_url)
        if response.status_code != 200:
            logger.error(f'"{self.source_name}" returned status code {response.status_code}')
            return posts_data
        self.rss_data_root = ET.fromstring(response.text)
        for rss_data_elem in self.rss_items_root():
            if self.item_tag_name in rss_data_elem.tag:
                dt = None
                title = None
                url = None
                brief = None
                for rss_data_subelem in rss_data_elem:
                    tag = rss_data_subelem.tag
                    text = rss_data_subelem.text
                    if self.title_tag_name in tag:
                        title = text.strip()
                    elif self.pubdate_tag_name in tag:
                        dt = dateutil.parser.parse(self._date_from_russian_to_english(text))
                    elif self.link_tag_name in tag:
                        if text:
                            url = text
                        elif 'href' in rss_data_subelem.attrib:
                            url = rss_data_subelem.attrib['href']
                        else:
                            logger.error(f'Could not find URL for "{title}" feed record')
                    elif self.description_tag_name in tag:
                        brief = text
                post_data = PostData(dt, title, self.process_url(url), brief)
                posts_data.append(post_data)
        return posts_data

    def _date_from_russian_to_english(self,
                                      datetime_text: str):
        days_map = {
            'Пн': 'Mon',
            'Вт': 'Tue',
            'Ср': 'Wed',
            'Чт': 'Thu',
            'Пт': 'Fri',
            'Сб': 'Sat',
            'Вс': 'Sun',
        }
        months_map = {
            'янв': 'jan',
            'фев': 'feb',
            'мар': 'mar',
            'апр': 'apr',
            'май': 'may',
            'мая': 'may',
            'июн': 'jun',
            'июл': 'jul',
            'авг': 'aug',
            'сен': 'sep',
            'окт': 'oct',
            'ноя': 'nov',
            'дек': 'dec',
        }
        converted_datetime_text = datetime_text
        for ru_en_map in (days_map, months_map):
            for ru, en in ru_en_map.items():
                converted_datetime_text = converted_datetime_text.replace(ru, en)
        return converted_datetime_text

    def process_url(self, url):
        return url

    @abstractmethod
    def rss_items_root(self):
        pass


class SimpleRssBasicParsingModule(RssBasicParsingModule):

    item_tag_name = 'item'
    title_tag_name = 'title'
    pubdate_tag_name = 'pubDate'
    link_tag_name = 'link'
    description_tag_name = 'description'

    def rss_items_root(self):
        return self.rss_data_root[0]


class OpenNetRuParsingModule(SimpleRssBasicParsingModule):

    source_name = "OpenNetRu"
    rss_url = 'https://www.opennet.ru/opennews/opennews_all_utf.rss'


class LinuxComParsingModule(SimpleRssBasicParsingModule):

    source_name = "LinuxCom"
    rss_url = 'https://www.linux.com/topic/feed/'


class OpenSourceComParsingModule(SimpleRssBasicParsingModule):
    # NOTE: Provider provides RSS feed for less than week, more regular check is needed

    source_name = 'OpenSourceCom'
    rss_url = 'https://opensource.com/feed'


class ItsFossComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ItsFossCom'
    rss_url = 'https://itsfoss.com/all-blog-posts/feed/'


class LinuxOrgRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxOrgRu'
    rss_url = 'https://www.linux.org.ru/section-rss.jsp?section=1'


class AnalyticsIndiaMagComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AnalyticsIndiaMagCom'
    rss_url = 'https://analyticsindiamag.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
        FiltrationType.GENERIC,
    ]


class ArsTechnicaComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ArsTechnicaCom'
    rss_url = 'https://arstechnica.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class HackadayComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HackadayCom'
    rss_url = 'https://hackaday.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class JaxenterComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'JaxenterCom'
    rss_url = 'https://jaxenter.com/rss'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class LinuxInsiderComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxInsiderCom'
    rss_url = 'https://linuxinsider.com/rss-feed'


class MashableComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MashableCom'
    rss_url = 'https://mashable.com/rss/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SdTimesComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SdTimesCom'
    rss_url = 'https://sdtimes.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SecurityBoulevardComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SecurityBoulevardCom'
    rss_url = 'https://securityboulevard.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SiliconAngleComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SiliconAngleCom'
    rss_url = 'https://siliconangle.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TechCrunchComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechCrunchCom'
    rss_url = 'https://techcrunch.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TechNodeComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechNodeCom'
    rss_url = 'https://technode.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TheNextWebComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheNextWebCom'
    rss_url = 'https://thenextweb.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class VentureBeatComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'VentureBeatCom'
    rss_url = 'https://venturebeat.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class ThreeDPrintingMediaNetworkParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ThreeDPrintingMediaNetwork'
    rss_url = 'https://www.3dprintingmedia.network/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class CbrOnlineComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CbrOnlineCom'
    rss_url = 'https://www.cbronline.com/rss'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class HelpNetSecurityComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HelpNetSecurityCom'
    rss_url = 'https://www.helpnetsecurity.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SecuritySalesComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SecuritySalesCom'
    rss_url = 'https://www.securitysales.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TechRadarComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechRadarCom'
    rss_url = 'https://www.techradar.com/rss'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TfirIoParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TfirIo'
    rss_url = 'https://www.tfir.io/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class ZdNetComLinuxParsingModule(SimpleRssBasicParsingModule):
    # TODO: Think about parsing other sections
    source_name = 'ZdNetComLinux'
    rss_url = 'https://www.zdnet.com/topic/linux/rss.xml'


class LinuxFoundationOrgParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxFoundationOrg'
    rss_url = 'https://linuxfoundation.org/rss'


class HabrComBasicParsingModule(SimpleRssBasicParsingModule):

    source_name = None
    hub_code = None

    @property
    def rss_url(self):
        return f'https://habr.com/ru/rss/hub/{self.hub_code}/all/?fl=ru'

    def process_url(self, url: str):
        return re.sub('/\?utm_campaign=.*&utm_source=habrahabr&utm_medium=rss',
                      '',
                      url)


class HabrComNewsParsingModule(HabrComBasicParsingModule):

    source_name = 'HabrComNews'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]

    @property
    def rss_url(self):
        return f'https://habr.com/ru/rss/news/'


class HabrComOpenSourceParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComOpenSource'
    hub_code = 'open_source'


class HabrComLinuxParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComLinux'
    hub_code = 'linux'


class HabrComLinuxDevParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComLinuxDev'
    hub_code = 'linux_dev'


class HabrComNixParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComNix'
    hub_code = 'nix'


class HabrComDevOpsParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComDevOps'
    hub_code = 'devops'


class HabrComSysAdmParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComSysAdm'
    hub_code = 'sys_admin'


class HabrComGitParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComGit'
    hub_code = 'git'


class YouTubeComBasicParsingModule(RssBasicParsingModule):

    source_name = None
    channel_id = None
    item_tag_name = 'entry'
    title_tag_name = 'title'
    pubdate_tag_name = 'published'
    link_tag_name = 'link'
    description_tag_name = 'description'

    def rss_items_root(self):
        return self.rss_data_root

    @property
    def rss_url(self):
        return f'https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}'


class YouTubeComAlekseySamoilovParsingModule(YouTubeComBasicParsingModule):

    source_name = f'YouTubeComAlekseySamoilov'
    channel_id = 'UC3kAbMcYr-JEMSb2xX4OdpA'


class LosstRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LosstRu'
    rss_url = 'https://losst.ru/rss'


class AstraLinuxRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AstraLinuxRu'
    rss_url = 'https://astralinux.ru/rss'


class BaseAltRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BaseAltRu'
    rss_url = 'https://www.basealt.ru/feed.rss'


class PingvinusRuParsingModule(BasicParsingModule):

    source_name = 'PingvinusRu'
    site_url = 'https://pingvinus.ru'

    def __init__(self):
        super().__init__()
        self.news_page_url = f'{self.site_url}/news'

    def _parse(self):
        response = requests.get(self.news_page_url)
        tree = html.fromstring(response.content)
        titles_blocks = tree.xpath('//div[@class="newsdateblock"]//h2/a[contains(@href, "/news/")]')
        dates_blocks = tree.xpath('//div[@class="newsdateblock"]//span[@class="time"]')
        if len(titles_blocks) != len(dates_blocks):
            raise Exception('News titles count does not match dates count')
        rel_urls = tree.xpath('//div[@class="newsdateblock"]//h2/a[contains(@href, "/news/")]/@href')
        titles_texts = [title_block.text for title_block in titles_blocks]
        dates_texts = [date_block.text for date_block in dates_blocks]
        urls = [f'{self.site_url}{rel_url}' for rel_url in rel_urls]
        posts = []
        for title, date_str, url in zip(titles_texts, dates_texts, urls):
            dt = datetime.datetime.strptime(date_str, '%d.%m.%Y')
            dt = dt.replace(tzinfo=dateutil.tz.gettz('Europe/Moscow'))
            post_data = PostData(dt, title, url, None)
            posts.append(post_data)
        return posts


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
