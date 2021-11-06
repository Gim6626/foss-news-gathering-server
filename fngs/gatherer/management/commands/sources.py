from typing import List, Tuple
from abc import ABCMeta, abstractmethod
import xml.etree.ElementTree as ET
from lxml import html
import requests
import re
from pprint import pprint
import traceback
import datetime
import dateutil
from copy import copy
import pytz

from gatherer.models import *


foss_news_project = Project.objects.get(name='FOSS News')
os_friday_project = Project.objects.get(name='OS Friday')
FOSS_NEWS_REGEXP = r'^FOSS News №\d+.*$'


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
                 brief: str,
                 filtered: bool = None):
        self.dt = dt
        self.title = title
        self.url = url
        self.brief = brief
        self.keywords = []
        self.filtered = None

    def __str__(self):
        return f'{self.dt} -- {self.url} -- {self.title} -- {shorten_text(self.brief)}'


class PostsData:

    def __init__(self,
                 source_name: str,
                 projects: List[Project],
                 posts_data_list: List[PostData],
                 language: Language,
                 filters: List['FiltrationType'],
                 warning: str = None):
        self.source_name = source_name
        self.projects = projects
        self.posts_data_list = posts_data_list
        self.language = language
        self.filters = filters
        self.warning = warning


class FiltrationType(Enum):
    GENERIC = 'generic'
    SPECIFIC = 'specific'


class ParsingResult:

    def __init__(self, overall_count, posts_data_after_filtration, source_enabled, source_error, parser_error):
        self.overall_count = overall_count
        self.posts_data_after_filtration: List[PostData] or None = posts_data_after_filtration
        self.source_enabled: bool = source_enabled
        self.source_error: str or None = source_error
        self.parser_error: str or None = parser_error

    @property
    def success(self):
        return not(self.source_error or self.parser_error)


class DigestSourceException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BasicParsingModule(metaclass=ABCMeta):

    data_url = None
    projects: Tuple[Project] = ()
    warning = None
    filtration_needed = False
    filters = []
    language: Language = None

    def __init__(self, logger):
        self.logger = logger

    @property
    def source_name(self):
        return self.__class__.__name__.replace('ParsingModule', '')

    @property
    def data_url(self):
        return DigestRecordsSource.objects.get(name=self.source_name).data_url

    def language(self):
        return DigestRecordsSource.objects.get(name=self.source_name).language

    def parse(self, days_count: int) -> ParsingResult:
        if not DigestRecordsSource.objects.get(name=self.source_name).enabled:  # TODO: Check existence
            self.logger.warning(f'"{self.source_name}" is disabled')
            return ParsingResult(0, [], False, None, None)
        try:
            posts_data: List[PostData] = self._parse()
        except DigestSourceException as e:
            self.logger.error(f'Failed to parse "{self.source_name}", source error: {str(e)}')
            return ParsingResult(0, [], True, str(e), None)
        except Exception as e:
            self.logger.error(f'Failed to parse "{self.source_name}", parser error: {str(e)}')
            self.logger.error(traceback.format_exc())
            return ParsingResult(0, [], True, None, str(e))
        try:
            filtered_posts_data: List[PostData] = self._filter_out(posts_data, days_count)
            self._fill_keywords(filtered_posts_data)
            return ParsingResult(len(posts_data), filtered_posts_data, True, None, None)
        except Exception as e:
            self.logger.error(f'Failed to filter data parsed from "{self.source_name}" source: {str(e)}')
            self.logger.error(traceback.format_exc())
            return ParsingResult(0, [], True, None, str(e))

    @abstractmethod
    def _parse(self) -> List[PostData]:
        pass

    def _fill_keywords(self, posts_data: List[PostData]):
        keywords_to_check = []
        keywords_to_check += [k.name for k in Keyword.objects.all()]
        for post_data in posts_data:
            for keyword in keywords_to_check:
                if keyword in post_data.keywords:
                    continue
                if BasicParsingModule.find_keyword_in_title(keyword, post_data.title):
                    post_data.keywords.append(keyword)

    @staticmethod
    def find_keyword_in_title(keyword, title):
        return re.search(rf'\b{re.escape(keyword)}\b', title, re.IGNORECASE)

    def _filter_out(self, source_posts_data: List[PostData], days_count: int):
        actual_posts_data = self._filter_out_old(source_posts_data, days_count)
        outdated_len = len(source_posts_data) - len(actual_posts_data)
        if outdated_len:
            self.logger.info(f'{len(source_posts_data) - len(actual_posts_data)}/{len(source_posts_data)} posts ignored for "{self.source_name}" as too old')
        filtered_posts_data = self._filter_out_by_keywords(actual_posts_data)
        nonactual_len = len(actual_posts_data) - len(filtered_posts_data)
        if nonactual_len:
            self.logger.info(f'{len(source_posts_data) - len(actual_posts_data)}/{len(source_posts_data)} posts ignored for "{self.source_name}" as not passed keywords filters')
        return filtered_posts_data

    def _filter_out_by_keywords(self, posts_data: List[PostData]):
        if not self.filtration_needed:
            return posts_data
        filtered_posts_data: List[PostData] = []
        keywords_to_check = []
        if FiltrationType.GENERIC in self.filters:
            keywords_to_check += [k.name for k in Keyword.objects.filter(is_generic=True, proprietary=False)]
        if FiltrationType.SPECIFIC in self.filters:
            keywords_to_check += [k.name for k in Keyword.objects.filter(is_generic=False, proprietary=False)]
        for post_data in posts_data:
            if not post_data.title:
                self.logger.error(f'Empty title for URL {post_data.url}')
                continue
            matched = False
            for keyword in keywords_to_check:
                if BasicParsingModule.find_keyword_in_title(keyword, post_data.title):
                    matched = True
                    break
            processed_post_data = copy(post_data)
            if matched:
                self.logger.debug(f'"{post_data.title}" from "{self.source_name}" added because it contains keywords {post_data.keywords}')
                processed_post_data.filtered = False
            else:
                self.logger.warning(f'"{post_data.title}" ({post_data.url}) from "{self.source_name}" filtered out cause not contains none of expected keywords')
                processed_post_data.filtered = True
            filtered_posts_data.append(processed_post_data)
        return filtered_posts_data

    def _filter_out_old(self, posts_data: List[PostData], days_count: int) -> List[PostData]:
        filtered_posts_data: List[PostData] = []
        dt_now = datetime.datetime.now(tz=dateutil.tz.tzlocal())
        already_existing_digest_records_dt_updated_count = 0
        for post_data in posts_data:
            if post_data.dt is not None and (dt_now - post_data.dt).days > days_count:
                self.logger.debug(f'"{post_data.title}" from "{self.source_name}" filtered as too old ({post_data.dt})')
                similar_records = DigestRecord.objects.filter(url=post_data.url)  # TODO: Replace check for similar records before and with "get"
                if similar_records:
                    if not similar_records[0].dt:
                        similar_records[0].dt = post_data.dt
                        self.logger.debug(f'{post_data.url} already exists in database, but without date, fix it')
                        already_existing_digest_records_dt_updated_count += 1
                        similar_records[0].save()
            else:
                filtered_posts_data.append(post_data)
        if already_existing_digest_records_dt_updated_count:
            self.logger.info(f'Few outdated sources found in database without dates, fixed for {already_existing_digest_records_dt_updated_count} sources')
        return filtered_posts_data


class RssBasicParsingModule(BasicParsingModule):

    item_tag_name = None
    title_tag_name = None
    pubdate_tag_name = None
    link_tag_name = None
    description_tag_name = None
    no_description = False

    def __init__(self, logger):
        self.rss_data_root = None
        super().__init__(logger)

    def _preprocess_xml(self, text: str):
        return text

    def _preprocess_date_str(self, date_str: str):
        return date_str

    def _parse(self):
        posts_data: List[PostData] = []
        response = requests.get(self.data_url,
                                headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'})
        if response.status_code != 200:
            raise DigestSourceException(f'"{self.source_name}" returned status code {response.status_code}')
        else:
            self.logger.debug(f'Successfully fetched RSS for "{self.source_name}"')
        self.rss_data_root = ET.fromstring(self._preprocess_xml(response.text))
        no_description_at_all = True
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
                        if not text:
                            continue
                        title = text.strip()
                    elif self.pubdate_tag_name in tag:
                        text = self._preprocess_date_str(text)
                        text = self._date_from_russian_to_english(text) # TODO: Extract such filter to specific classes
                        dt: datetime.datetime = dateutil.parser.parse(text)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=pytz.UTC)
                    elif self.link_tag_name in tag:
                        if text:
                            url = text
                        elif 'href' in rss_data_subelem.attrib:
                            url = rss_data_subelem.attrib['href']
                        else:
                            self.logger.error(f'Could not find URL for "{title}" feed record')
                    elif self.description_tag_name in tag:
                        brief = text
                        no_description_at_all = False
                    elif 'group' in tag:
                        for rss_data_subsubelem in rss_data_subelem:
                            subtag = rss_data_subsubelem.tag
                            if self.description_tag_name in subtag:
                                subtext = rss_data_subsubelem.text
                                brief = subtext
                                no_description_at_all = False
                url = self.process_url(url)
                if not url:
                    if title:
                        self.logger.error(f'Empty URL for title "{title}" for source "{self.source_name}"')
                    else:
                        self.logger.error(f'Empty URL and empty title for source "{self.source_name}"')
                    continue
                post_data = PostData(dt, title, url, brief)
                posts_data.append(post_data)
        if posts_data and no_description_at_all and not self.no_description:
            self.logger.error(f'No descriptions at all in {self.source_name} source feed')
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
    pass


class LinuxComParsingModule(SimpleRssBasicParsingModule):
    pass


class OpenSourceComParsingModule(SimpleRssBasicParsingModule):
    pass


class ItsFossComParsingModule(SimpleRssBasicParsingModule):
    pass


class LinuxOrgRuParsingModule(SimpleRssBasicParsingModule):
    pass


class AnalyticsIndiaMagComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class ArsTechnicaComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class HackadayComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class JaxenterComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LinuxInsiderComParsingModule(SimpleRssBasicParsingModule):
    pass


class MashableComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    language = Language.ENGLISH


class SdTimesComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SecurityBoulevardComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SiliconAngleComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TechCrunchComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TechNodeComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TheNextWebComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class VentureBeatComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class ThreeDPrintingMediaNetworkParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CbrOnlineComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class HelpNetSecurityComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SecuritySalesComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TechRadarComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TfirIoParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class ZdNetComLinuxParsingModule(SimpleRssBasicParsingModule):
    # TODO: Think about parsing other sections
    pass


class LinuxFoundationOrgParsingModule(SimpleRssBasicParsingModule):
    pass


class HabrComBasicParsingModule(SimpleRssBasicParsingModule):

    def process_url(self, url: str):
        return re.sub('/\?utm_campaign=.*&utm_source=habrahabr&utm_medium=rss',
                      '',
                      url)


class HabrComNewsParsingModule(HabrComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FilterFossNewsItselfMixin:

    def filter_foss_news_itself(self, posts_data: List[PostData]):
        for post_data in posts_data:
            if re.fullmatch(FOSS_NEWS_REGEXP, post_data.title):
                self.logger.warning(f'Filtered "{post_data.title}" as it is our digest itself')
                post_data.filtered = True
        return posts_data


class HabrComOpenSourceParsingModule(HabrComBasicParsingModule,
                                     FilterFossNewsItselfMixin):

    def _parse(self):
        posts_data: List[PostData] = super()._parse()
        filtered_posts_data = self.filter_foss_news_itself(posts_data)
        return filtered_posts_data


class HabrComLinuxParsingModule(HabrComBasicParsingModule):
    pass


class HabrComLinuxDevParsingModule(HabrComBasicParsingModule):
    pass


class HabrComNixParsingModule(HabrComBasicParsingModule,
                              FilterFossNewsItselfMixin):

    def _parse(self):
        posts_data: List[PostData] = super()._parse()
        filtered_posts_data = self.filter_foss_news_itself(posts_data)
        return filtered_posts_data


class HabrComDevOpsParsingModule(HabrComBasicParsingModule):
    pass


class HabrComSysAdmParsingModule(HabrComBasicParsingModule):
    pass


class HabrComGitParsingModule(HabrComBasicParsingModule):
    pass


class YouTubeComBasicParsingModule(RssBasicParsingModule):

    item_tag_name = 'entry'
    title_tag_name = 'title'
    pubdate_tag_name = 'published'
    link_tag_name = 'link'
    description_tag_name = 'description'

    def rss_items_root(self):
        return self.rss_data_root


class YouTubeComAlekseySamoilovParsingModule(YouTubeComBasicParsingModule):
    pass


class PlafonAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class TheLinuxExperimentAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class NikolayIvanovichAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class SwitchedToLinuxAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class LearnLinuxTVAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class DmitryRobionekAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class LosstRuParsingModule(SimpleRssBasicParsingModule):
    pass


class AstraLinuxRuParsingModule(SimpleRssBasicParsingModule):

    no_description = True


class BaseAltRuParsingModule(SimpleRssBasicParsingModule):

    _BASE_URL = 'https://www.basealt.ru'

    def process_url(self, url):
        if self._BASE_URL not in url:
            self.logger.info(f'Relative URL found "{url}", prepending with base url "{self._BASE_URL}"')
            return f'{self._BASE_URL}{url}'
        else:
            return url


class PingvinusRuParsingModule(BasicParsingModule):

    def __init__(self, logger):
        super().__init__(logger)
        self.news_page_url = f'{self.data_url}/news'

    def _parse(self):
        response = requests.get(self.news_page_url)
        if response.status_code != 200:
            raise DigestSourceException(f'"{self.source_name}" returned status code {response.status_code}')
        tree = html.fromstring(response.content)
        titles_blocks = tree.xpath('//div[@class="newsdateblock"]//h2/a[contains(@href, "/news/")]')
        dates_blocks = tree.xpath('//div[@class="newsdateblock"]//span[@class="time"]')
        if len(titles_blocks) != len(dates_blocks):
            raise Exception('News titles count does not match dates count')
        rel_urls = tree.xpath('//div[@class="newsdateblock"]//h2/a[contains(@href, "/news/")]/@href')
        titles_texts = [title_block.text for title_block in titles_blocks]
        dates_texts = [date_block.text for date_block in dates_blocks]
        urls = [f'{self.data_url}{rel_url}' for rel_url in rel_urls]
        posts = []
        for title, date_str, url in zip(titles_texts, dates_texts, urls):
            dt = datetime.datetime.strptime(date_str, '%d.%m.%Y')
            dt = dt.replace(tzinfo=dateutil.tz.gettz('Europe/Moscow'))
            if not title:
                self.logger.error(f'Empty title for URL {url}')
                continue
            post_data = PostData(dt, title, url, None)
            posts.append(post_data)
        return posts


class RedditRssBasicParsingModule(SimpleRssBasicParsingModule):

    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class OpenSourceOnRedditParsingModule(RedditRssBasicParsingModule):
    pass


class LinuxGnuLinuxFreeSoftwareParsingModule(RedditRssBasicParsingModule):
    pass


class ContainerJournalParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class BlogCloudNativeComputingFoundationParsingModule(SimpleRssBasicParsingModule):
    pass


class KubedexComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CiliumBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class EngineeringDockerBlogParsingModule(SimpleRssBasicParsingModule):
    pass


class BlogSysdigParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CodefreshParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AquaBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AmbassadorApiGatewayParsingModule(SimpleRssBasicParsingModule):

    description_tag_name = 'content'
    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class WeaveworksParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class KubeweeklyArchiveFeedParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LachlanEvensonParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class UnixWayAtYouTubeParsingModule(YouTubeComBasicParsingModule):
    pass


class SoftwareDefinedTalkParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class PrometheusBlogParsingModule(SimpleRssBasicParsingModule):

    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class SysdigParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class InnovateEverywhereOnRancherLabsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TheNewStackPodcastParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class KubernetesOnMediumParsingModule(SimpleRssBasicParsingModule):
    pass


class RamblingsFromJessieParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class DiscussKubernetesLatestTopicsParsingModule(SimpleRssBasicParsingModule):
    pass


class ProjectCalicoParsingModule(SimpleRssBasicParsingModule):
    pass


class LastWeekInKubernetesDevelopmentParsingModule(SimpleRssBasicParsingModule):

    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class KubernetesParsingModule(RedditRssBasicParsingModule):
    pass


class EnvoyProxyParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'content'


class TheNewStackAnalystsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TigeraParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TwistlockParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class BlogOnRancherLabsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TheNewStackParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class KonghqParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class DockerOnMediumParsingModule(SimpleRssBasicParsingModule):
    pass


class DockerBlogParsingModule(SimpleRssBasicParsingModule):
    pass


class DiscussKubernetesLatestPostsParsingModule(SimpleRssBasicParsingModule):
    pass


class D2IqBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class PodctlEnterpriseKubernetesParsingModule(SimpleRssBasicParsingModule):
    pass


class IstioBlogAndNewsParsingModule(SimpleRssBasicParsingModule):

    def _parse(self):
        posts_data: List[PostData] = super()._parse()
        posts_data_with_fixed_urls = []
        for p in posts_data:
            if not re.fullmatch(r'^https://.*', p.url):
                p.url = f'https://istio.io{p.url}'
            posts_data_with_fixed_urls.append(p)
        return posts_data_with_fixed_urls


class ProgrammingKubernetesParsingModule(SimpleRssBasicParsingModule):

    description_tag_name = 'content'


class KubernetesPodcastFromGoogleParsingModule(SimpleRssBasicParsingModule):
    pass


class CloudNativeComputingFoundationParsingModule(SimpleRssBasicParsingModule):
    pass


class BlogOnStackroxSecurityBuiltInParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class RecentQuestionsOpenSourceStackExchangeParsingModule(SimpleRssBasicParsingModule):

    description_tag_name = 'summary'
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'

    def rss_items_root(self):
        return self.rss_data_root


class LxerLinuxNewsParsingModule(SimpleRssBasicParsingModule):

    pubdate_tag_name = 'date'

    def rss_items_root(self):
        return self.rss_data_root


class NativecloudDevParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LinuxlinksParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LobstersJavaJavaProgrammingParsingModule(SimpleRssBasicParsingModule):
    pass


class FlossWeeklyVideoParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )

    def _preprocess_date_str(self, date_str: str):
        return super()._preprocess_date_str(date_str.replace('PDT', 'UTC-07'))


class LobstersNodejsNodeJsProgrammingParsingModule(SimpleRssBasicParsingModule):
    pass


class OpenSourceOnMediumParsingModule(SimpleRssBasicParsingModule):
    pass


class BlogOnSmallstepParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LinuxNotesFromDarkduckParsingModule(SimpleRssBasicParsingModule):
    pass


class MicrosoftOpenSourceStoriesParsingModule(SimpleRssBasicParsingModule):

    description_tag_name = 'content'


class LobstersUnixNixParsingModule(SimpleRssBasicParsingModule):
    pass


class AmericanExpressTechnologyParsingModule(SimpleRssBasicParsingModule):

    item_tag_name = 'entry'
    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class NewestOpenSourceQuestionsFeedParsingModule(SimpleRssBasicParsingModule):

    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'summary'

    def rss_items_root(self):
        return self.rss_data_root


class TeejeetechParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FreedomPenguinParsingModule(SimpleRssBasicParsingModule):
    pass


class LobstersLinuxLinuxParsingModule(SimpleRssBasicParsingModule):
    pass


class CrunchToolsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LinuxUprisingBlogParsingModule(SimpleRssBasicParsingModule):

    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class EaglemanBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class DbakevlarParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class EngblogRuParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LobstersDotnetCFNetProgrammingParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LobstersWebWebDevelopmentAndNewsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MorningDewByAlvinAshcraftParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LobstersSecurityNetsecAppsecAndInfosecParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SamJarManParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LobstersDistributedDistributedSystemsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class LobstersDevopsDevopsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class DevRelWeeklyParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AzureAdvocatesContentWrapUpParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FlantBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class ThoughtworksInsightsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'summary'

    item_tag_name = 'entry'

    def rss_items_root(self):
        return self.rss_data_root


class LobstersOsdevOperatingSystemDesignAndDevelopmentWhenNoSpecificOsTagExistsParsingModule(SimpleRssBasicParsingModule):
    pass


class MicrosoftDevradioParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class NewBlogArticlesInMicrosoftTechCommunityParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FosslifeParsingModule(SimpleRssBasicParsingModule):
    pass


class AzureInfohubRssAzureParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class PerformanceIsAFeatureParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )

    item_tag_name = 'entry'
    pubdate_tag_name = 'updated'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class LobstersWasmWebassemblyParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TheCommunityRoundtableParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class Rss20TaggedMobileMobileAppWebDevelopmentParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AwsArchitectureBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class HeptioUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AlexEllisOpenfaasCommunityAwesomenessOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class VmwareCloudNativeAppsUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class D2IqParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TigeraUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CncfCloudNativeComputingFoundationUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):
    pass


class CephUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):
    pass


class RookRookPresentationsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class DockerParsingModule(SimpleRssBasicParsingModule):
    pass


class RookUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CncfCloudNativeComputingFoundationParsingModule(YouTubeComBasicParsingModule):
    pass


class WeaveworksIncWeaveOnlineUserGroupsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class KubernautsIoUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):
    pass


class AlexEllisUploadsOnYoutubeParsingModule(YouTubeComBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CephCephTestingWeeklyOnYoutubeParsingModule(YouTubeComBasicParsingModule):
    pass


class NetCurryRecentArticlesParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class ThreeHundredSixtyDegreeDbProgrammingParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'content'

    item_tag_name = 'entry'

    def rss_items_root(self):
        return self.rss_data_root


class FourSysopsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AProgrammerWithMicrosoftToolsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AarononthewebParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AllanSBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AndyGibsonParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AntonioSBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class ArcaneCodeParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AugustoAlvarezParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class Channel9ParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CloudComputingBigDataHpcCodeinstinctParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class ClusteringForMereMortalsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class CommandLineFanaticParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )

    def _preprocess_date_str(self, date_str: str):
        return super()._preprocess_date_str(date_str.replace('- 0700', 'UTC-07'));


class DevcurryParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class DonTBeIffyParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'content'


class ElegantCodeParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FelipeOliveiraParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FromRavikanthSBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class FullFeedParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class GauravmantriComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class GeekSucksParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class GoodCodersCodeGreatReuseParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class GunnarPeipmanSAspNetBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'content'


class HanselminutesParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class HelpDeskGeekHelpDeskTipsForItProsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class HenrikOlssonSComputerSoftwareNotesParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class HongkiatComParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class IcosmogeekParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    description_tag_name = 'content'


class InDepthFeaturesParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class JenkovComNewsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class JonathanGKoomeyPhDParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class KScottAllenParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MaartenBalliauwBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MarceloSincicMvpParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MartinFowlerParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'updated'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class MaxTrinidadThePowershellFrontParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MethodOfFailedByTimHeuerParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MichaelCrumpParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class NewsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class PetriItKnowledgebaseParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class PrecisionComputingParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class PublisherSRoundUpParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class RandsInReposeParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class RedmondReportParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class RhyousParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class RichardSeroterSArchitectureMusingsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class RickStrahlSWebLogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SdmSoftwareParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SecretgeekParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )

    def _preprocess_xml(self, text: str):
        return super()._preprocess_xml(text.replace('ï»¿', ''))


class ShawnWildermuthSBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'updated'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class SimpleTalkRssFeedParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SmashingMagazineFeedParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class SteveSmithSBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TechgenixNewsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TecosystemsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TheArtOfSimplicityParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class TheExptaBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class TheMicrosoftPlatformParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class ThinkingInSoftwareParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class VirtualisationManagementBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class VisioGuyParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class WebcastsParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class WindowsPowershellBlogParsingModule(SimpleRssBasicParsingModule):
    pass


class WindowsServerDivisionWeblogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class YouAreNotSoSmartParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class YouVeBeenHaackedParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class AlexanderBindyuBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )

    def _preprocess_date_str(self, date_str: str):
        return super()._preprocess_date_str(date_str.replace('PST', 'UTC-08'))


class ScottHanselmanSBlogParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class AndreyOnNetParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class MyInformationResourceBlogMirNetParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )
    item_tag_name = 'entry'
    pubdate_tag_name = 'published'
    description_tag_name = 'content'

    def rss_items_root(self):
        return self.rss_data_root


class EternalArrivalParsingModule(SimpleRssBasicParsingModule):

    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class Rss20TaggedMerkleTreesAndRelatedSimilarDataStructuresNotBusinessScamNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Rss20TaggedMerkleTreesAndRelatedSimilarDataStructuresNotBusinessScamNews'
    projects = (
        os_friday_project,
    )
    data_url = 'https://lobste.rs/t/merkle-trees.rss'
    language = Language.ENGLISH
    filtration_needed = True
    filters = (
        FiltrationType.SPECIFIC,
    )


class WeeklyOsmParsingModule(SimpleRssBasicParsingModule):
    pass
