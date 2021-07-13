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

from gatherer.models import *
from .logger import logger
from .keywords import keywords


foss_news_project = Project.objects.get(name='FOSS News')
os_friday_project = Project.objects.get(name='OS Friday')


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
                 projects: List[Project],
                 posts_data_list: List[PostData],
                 warning: str = None):
        self.source_name = source_name
        self.projects = projects
        self.posts_data_list = posts_data_list
        self.warning = warning


class FiltrationType(Enum):
    GENERIC = 'generic'
    SPECIFIC = 'specific'


class BasicParsingModule(metaclass=ABCMeta):

    source_name = None
    projects: Tuple[Project] = ()
    warning = None
    filtration_needed = False
    filters = []

    def parse(self, days_count: int) -> List[PostData]:
        try:
            posts_data: List[PostData] = self._parse()
        except Exception as e:
            logger.error(f'Failed to parse "{self.source_name}" source: {str(e)}')
            logger.error(traceback.format_exc())
            return []
        try:
            filtered_posts_data: List[PostData] = self._filter_out(posts_data, days_count)
            self._fill_keywords(filtered_posts_data)
            return filtered_posts_data
        except Exception as e:
            logger.error(f'Failed to filter data parsed from "{self.source_name}" source: {str(e)}')
            logger.error(traceback.format_exc())
            return []

    @abstractmethod
    def _parse(self) -> List[PostData]:
        pass

    def _fill_keywords(self, posts_data: List[PostData]):
        keywords_to_check = []
        keywords_to_check += keywords['generic']
        keywords_to_check += keywords['specific']
        for post_data in posts_data:
            for keyword in keywords_to_check:
                if keyword in post_data.keywords:
                    continue
                if self._find_keyword_in_title(keyword, post_data.title):
                    post_data.keywords.append(keyword)

    def _find_keyword_in_title(self, keyword, title):
        return re.search(rf'\b{re.escape(keyword)}\b', title, re.IGNORECASE)

    def _filter_out(self, posts_data: List[PostData], days_count: int):
        filtered_posts_data: List[PostData] = posts_data
        filtered_posts_data = self._filter_out_old(filtered_posts_data, days_count)
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
                if self._find_keyword_in_title(keyword, post_data.title):
                    matched = True
                    break
            if matched:
                logger.debug(f'"{post_data.title}" from "{self.source_name}" added because it contains keywords {post_data.keywords}')
                filtered_posts_data.append(post_data)
            else:
                logger.warning(f'"{post_data.title}" ({post_data.url}) from "{self.source_name}" filtered out cause not contains none of expected keywords')
        return filtered_posts_data

    def _filter_out_old(self, posts_data: List[PostData], days_count: int) -> List[PostData]:
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
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.opennet.ru/opennews/opennews_all_utf.rss'


class LinuxComParsingModule(SimpleRssBasicParsingModule):

    source_name = "LinuxCom"
    projects = (
        foss_news_project,
        os_friday_project,
    )
    rss_url = 'https://www.linux.com/topic/feed/'


class OpenSourceComParsingModule(SimpleRssBasicParsingModule):
    # NOTE: Provider provides RSS feed for less than week, more regular check is needed

    source_name = 'OpenSourceCom'
    projects = (
        foss_news_project,
        os_friday_project
    )
    rss_url = 'https://opensource.com/feed'


class ItsFossComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ItsFossCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://itsfoss.com/all-blog-posts/feed/'


class LinuxOrgRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxOrgRu'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.linux.org.ru/section-rss.jsp?section=1'


class AnalyticsIndiaMagComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AnalyticsIndiaMagCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://analyticsindiamag.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
        FiltrationType.GENERIC,
    ]


class ArsTechnicaComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ArsTechnicaCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://arstechnica.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class HackadayComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HackadayCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://hackaday.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class JaxenterComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'JaxenterCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://jaxenter.com/rss'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class LinuxInsiderComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxInsiderCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://linuxinsider.com/rss-feed'


class MashableComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MashableCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://mashable.com/rss/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SdTimesComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SdTimesCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://sdtimes.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SecurityBoulevardComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SecurityBoulevardCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://securityboulevard.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SiliconAngleComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SiliconAngleCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://siliconangle.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TechCrunchComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechCrunchCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://techcrunch.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TechNodeComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechNodeCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://technode.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TheNextWebComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheNextWebCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://thenextweb.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class VentureBeatComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'VentureBeatCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://venturebeat.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class ThreeDPrintingMediaNetworkParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ThreeDPrintingMediaNetwork'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.3dprintingmedia.network/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class CbrOnlineComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CbrOnlineCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.cbronline.com/rss'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class HelpNetSecurityComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HelpNetSecurityCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.helpnetsecurity.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class SecuritySalesComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SecuritySalesCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.securitysales.com/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TechRadarComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechRadarCom'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.techradar.com/rss'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class TfirIoParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TfirIo'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.tfir.io/feed/'
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]


class ZdNetComLinuxParsingModule(SimpleRssBasicParsingModule):
    # TODO: Think about parsing other sections
    source_name = 'ZdNetComLinux'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.zdnet.com/topic/linux/rss.xml'


class LinuxFoundationOrgParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxFoundationOrg'
    projects = (
        foss_news_project,
    )
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
    projects = (
        foss_news_project,
    )
    filtration_needed = True
    filters = [
        FiltrationType.SPECIFIC,
    ]

    @property
    def rss_url(self):
        return f'https://habr.com/ru/rss/news/'


class HabrComOpenSourceParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComOpenSource'
    projects = (
        foss_news_project,
    )
    hub_code = 'open_source'


class HabrComLinuxParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComLinux'
    projects = (
        foss_news_project,
    )
    hub_code = 'linux'


class HabrComLinuxDevParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComLinuxDev'
    projects = (
        foss_news_project,
    )
    hub_code = 'linux_dev'


class HabrComNixParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComNix'
    projects = (
        foss_news_project,
    )
    hub_code = 'nix'


class HabrComDevOpsParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComDevOps'
    projects = (
        foss_news_project,
    )
    hub_code = 'devops'


class HabrComSysAdmParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComSysAdm'
    projects = (
        foss_news_project,
    )
    hub_code = 'sys_admin'


class HabrComGitParsingModule(HabrComBasicParsingModule):

    source_name = f'HabrComGit'
    projects = (
        foss_news_project,
    )
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
    projects = (
        foss_news_project,
    )
    channel_id = 'UC3kAbMcYr-JEMSb2xX4OdpA'


class LosstRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LosstRu'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://losst.ru/rss'


class AstraLinuxRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AstraLinuxRu'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://astralinux.ru/rss'


class BaseAltRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BaseAltRu'
    projects = (
        foss_news_project,
    )
    rss_url = 'https://www.basealt.ru/feed.rss'


class PingvinusRuParsingModule(BasicParsingModule):

    source_name = 'PingvinusRu'
    projects = (
        foss_news_project,
    )
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
            post_data = PostData(dt, title, self.projects, url, None)
            posts.append(post_data)
        return posts


class OpenSourceOnRedditParsingModule(SimpleRssBasicParsingModule):

    source_name = 'OpenSourceOnReddit'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.reddit.com/r/opensource/.rss'


class LinuxGnuLinuxFreeSoftwareParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxGnuLinuxFreeSoftware'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.reddit.com/r/linux/.rss'


class ContainerJournalParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ContainerJournal'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://containerjournal.com/feed/'


class BlogCloudNativeComputingFoundationParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BlogCloudNativeComputingFoundation'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://cncf.io/blog/feed'


class KubedexComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'KubedexCom'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://kubedex.com/feed/'


class CiliumBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CiliumBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://cilium.io/blog/rss.xml'


class EngineeringDockerBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'EngineeringDockerBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.docker.com/category/engineering/feed/'


class BlogSysdigParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BlogSysdig'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://sysdig.com/blog/feed/'


class CodefreshParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Codefresh'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blog.codefresh.io/rss/'


class AquaBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AquaBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blog.aquasec.com/rss.xml'


class AmbassadorApiGatewayParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AmbassadorApiGateway'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.getambassador.io/feed'


class WeaveworksParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Weaveworks'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.weave.works/blog/'


class KubeweeklyArchiveFeedParsingModule(SimpleRssBasicParsingModule):

    source_name = 'KubeweeklyArchiveFeed'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://us10.campaign-archive.com/feed?u=3885586f8f1175194017967d6&id=11c1b8bcb2'


class LachlanEvensonParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LachlanEvenson'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCC5NsnXM2lE6kKfJKdQgsRQ'


class SoftwareDefinedTalkParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SoftwareDefinedTalk'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/DrunkAndRetiredcomPodcast'


class PrometheusBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'PrometheusBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://prometheus.io/blog/feed.xml'


class SysdigParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Sysdig'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://sysdig.com/feed/'


class InnovateEverywhereOnRancherLabsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'InnovateEverywhereOnRancherLabs'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://rancher.com/feed/'


class TheNewStackPodcastParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheNewStackPodcast'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.soundcloud.com/users/soundcloud:users:107605642/sounds.rss'


class KubernetesOnMediumParsingModule(SimpleRssBasicParsingModule):

    source_name = 'KubernetesOnMedium'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://medium.com/feed/tag/kubernetes'


class RamblingsFromJessieParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RamblingsFromJessie'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.jessfraz.com/index.xml'


class DiscussKubernetesLatestTopicsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'DiscussKubernetesLatestTopics'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://discuss.kubernetes.io/latest.rss'


class ProjectCalicoParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ProjectCalico'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.projectcalico.org/feed/'


class LastWeekInKubernetesDevelopmentParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LastWeekInKubernetesDevelopment'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://lwkd.info/feed.xml'


class KubernetesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Kubernetes'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.reddit.com/r/kubernetes/.rss'


class EnvoyProxyParsingModule(SimpleRssBasicParsingModule):

    source_name = 'EnvoyProxy'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.envoyproxy.io/feed'


class TheNewStackAnalystsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheNewStackAnalysts'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.soundcloud.com/users/soundcloud:users:94518611/sounds.rss'


class TigeraParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Tigera'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.tigera.io/feed'


class TwistlockParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Twistlock'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.twistlock.com/feed/'


class BlogOnRancherLabsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BlogOnRancherLabs'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://rancher.com/blog/index.xml'


class TheNewStackParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheNewStack'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://thenewstack.io/feed/'


class KonghqParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Konghq'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://konghq.com/feed/'


class DockerOnMediumParsingModule(SimpleRssBasicParsingModule):

    source_name = 'DockerOnMedium'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://medium.com/feed/tag/docker'


class DockerBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'DockerBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blog.docker.io/feed/'


class DiscussKubernetesLatestPostsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'DiscussKubernetesLatestPosts'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://discuss.kubernetes.io/posts.rss'


class D2IqBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'D2IqBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://mesosphere.io/blog/atom.xml'


class PodctlEnterpriseKubernetesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'PodctlEnterpriseKubernetes'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.buzzsprout.com/110399.rss'


class IstioBlogAndNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'IstioBlogAndNews'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://istio.io/feed.xml'


class ProgrammingKubernetesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ProgrammingKubernetes'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://medium.com/feed/programming-kubernetes'


class KubernetesPodcastFromGoogleParsingModule(SimpleRssBasicParsingModule):

    source_name = 'KubernetesPodcastFromGoogle'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://kubernetespodcast.com/feeds/audio.xml'


class CloudNativeComputingFoundationParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CloudNativeComputingFoundation'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.cncf.io/feed'


class BlogOnStackroxSecurityBuiltInParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BlogOnStackroxSecurityBuiltIn'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.stackrox.com/post/index.xml'


class RecentQuestionsOpenSourceStackExchangeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RecentQuestionsOpenSourceStackExchange'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://opensource.stackexchange.com/feeds'


class LxerLinuxNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LxerLinuxNews'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://lxer.com/module/newswire/headlines.rss'


class NativecloudDevParsingModule(SimpleRssBasicParsingModule):

    source_name = 'NativecloudDev'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.nativecloud.dev/rss/'


class LinuxlinksParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Linuxlinks'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.linuxlinks.com/feed/'


class LobstersJavaJavaProgrammingParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersJavaJavaProgramming'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/java.rss'


class FlossWeeklyVideoParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FlossWeeklyVideo'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.twit.tv/floss_video_hd.xml'


class LobstersNodejsNodeJsProgrammingParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersNodejsNodeJsProgramming'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/nodejs.rss'


class OpenSourceOnMediumParsingModule(SimpleRssBasicParsingModule):

    source_name = 'OpenSourceOnMedium'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://medium.com/feed/tag/open-source'


class BlogOnSmallstepParsingModule(SimpleRssBasicParsingModule):

    source_name = 'BlogOnSmallstep'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://smallstep.com/blog/index.xml'


class LinuxNotesFromDarkduckParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxNotesFromDarkduck'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/LinuxNotesFromDarkduck'


class MicrosoftOpenSourceStoriesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MicrosoftOpenSourceStories'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://medium.com/feed/microsoft-open-source-stories'


class LobstersUnixNixParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersUnixNix'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/unix.rss'


class AmericanExpressTechnologyParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AmericanExpressTechnology'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://americanexpress.io/feed.xml'


class NewestOpenSourceQuestionsFeedParsingModule(SimpleRssBasicParsingModule):

    source_name = 'NewestOpenSourceQuestionsFeed'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://stackoverflow.com/feeds/tag?tagnames=open-source&sort=newest'


class TeejeetechParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Teejeetech'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://teejeetech.blogspot.com/feeds/posts/default'


class FreedomPenguinParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FreedomPenguin'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/FreedomPenguin'


class LobstersLinuxLinuxParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersLinuxLinux'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/linux.rss'


class CrunchToolsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CrunchTools'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://crunchtools.com/feed/'


class LinuxUprisingBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LinuxUprisingBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://feeds.feedburner.com/LinuxUprising'


class EaglemanBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'EaglemanBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.eagleman.com/blog?format=feed&type=rss'


class DbakevlarParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Dbakevlar'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://dbakevlar.com/feed/'


class EngblogRuParsingModule(SimpleRssBasicParsingModule):

    source_name = 'EngblogRu'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/engblogru'


class LobstersDotnetCFNetProgrammingParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersDotnetCFNetProgramming'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/dotnet.rss'


class LobstersWebWebDevelopmentAndNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersWebWebDevelopmentAndNews'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/web.rss'


class MorningDewByAlvinAshcraftParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MorningDewByAlvinAshcraft'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds2.feedburner.com/alvinashcraft'


class LobstersSecurityNetsecAppsecAndInfosecParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersSecurityNetsecAppsecAndInfosec'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/security.rss'


class BlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Blog'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.samjarman.co.nz/blog?format=RSS'


class LobstersDistributedDistributedSystemsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersDistributedDistributedSystems'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/distributed.rss'


class LobstersDevopsDevopsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersDevopsDevops'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/devops.rss'


class RssParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Rss'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://devrelweekly.com/issues.rss'


class AzureAdvocatesContentWrapUpParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AzureAdvocatesContentWrapUp'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.onazure.today/feed.xml'


class FlantBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FlantBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://blog.flant.com/feed/'


class ThoughtworksInsightsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ThoughtworksInsights'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.thoughtworks.com/rss/insights.xml'


class LobstersOsdevOperatingSystemDesignAndDevelopmentWhenNoSpecificOsTagExistsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersOsdevOperatingSystemDesignAndDevelopmentWhenNoSpecificOsTagExists'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/osdev.rss'


class MicrosoftDevradioParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MicrosoftDevradio'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCYjPVPCNwQyfbQEKlJ4ChHg'


class NewBlogArticlesInMicrosoftTechCommunityParsingModule(SimpleRssBasicParsingModule):

    source_name = 'NewBlogArticlesInMicrosoftTechCommunity'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://techcommunity.microsoft.com/gxcuf89792/rss/Community?interaction.style=blog'


class FosslifeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Fosslife'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.fosslife.org/rss.xml'


class AzureInfohubRssAzureParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AzureInfohubRssAzure'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://azureinfohub.azurewebsites.net/Feed?serviceTitle=Azure'


class PerformanceIsAFeatureParsingModule(SimpleRssBasicParsingModule):

    source_name = 'PerformanceIsAFeature'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://mattwarren.org/atom.xml'


class LobstersWasmWebassemblyParsingModule(SimpleRssBasicParsingModule):

    source_name = 'LobstersWasmWebassembly'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/wasm.rss'


class TheCommunityRoundtableParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheCommunityRoundtable'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://communityroundtable.com/feed/'


class Rss20TaggedMobileMobileAppWebDevelopmentParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Rss20TaggedMobileMobileAppWebDevelopment'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/mobile.rss'


class AwsArchitectureBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AwsArchitectureBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.awsarchitectureblog.com/atom.xml'


class HeptioUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HeptioUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UUjQU5ZI2mHswy7OOsii_URg'


class AlexEllisOpenfaasCommunityAwesomenessOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AlexEllisOpenfaasCommunityAwesomenessOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=PLlIapFDp305Cw4Mu13Oq--AEk0G0WXPO-'


class VmwareCloudNativeAppsUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'VmwareCloudNativeAppsUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UUdkGV51Nu0unDNT58bHt9bg'


class D2IqParsingModule(SimpleRssBasicParsingModule):

    source_name = 'D2Iq'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCxwCmgwyM7xtHaRULN6-dxg'


class TigeraUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TigeraUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UU8uN3yhpeBeerGNwDiQbcgw'


class CncfCloudNativeComputingFoundationUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CncfCloudNativeComputingFoundationUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UUvqbFHwN-nwalWPjPUKpvTA'


class CephUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CephUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UUno-Fry25FJ7B4RycCxOtfw'


class RookRookPresentationsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RookRookPresentationsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=PLP0uDo-ZFnQOCpYx1_uVCrx_bmyq7tdKr'


class DockerParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Docker'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UC76AVf2JkrwjxNKMuPpscHQ'


class RookUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RookUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UUa7kFUSGO4NNSJV8MJVlJAA'


class CncfCloudNativeComputingFoundationParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CncfCloudNativeComputingFoundation'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCvqbFHwN-nwalWPjPUKpvTA'


class WeaveworksIncWeaveOnlineUserGroupsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'WeaveworksIncWeaveOnlineUserGroupsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=PL9lTuCFNLaD0wEsbqf6IrGCWvZIAIo9cW'


class KubernautsIoUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'KubernautsIoUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UU5NDQ4F0JPQozyqnh1mghHQ'


class AlexEllisUploadsOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AlexEllisUploadsOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=UUJsK5Zbq0dyFZUBtMTHzxjQ'


class CephCephTestingWeeklyOnYoutubeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CephCephTestingWeeklyOnYoutube'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://www.youtube.com/playlist?list=PLrBUGiINAakMV7gKMQjFvcWL3PeY0y0lq'


class NetCurryRecentArticlesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'NetCurryRecentArticles'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/netCurryRecentArticles'


class ThreeHundredSixtyDegreeDbProgrammingParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ThreeHundredSixtyDegreeDbProgramming'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://db360.blogspot.com/feeds/posts/default'


class FourSysopsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FourSysops'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://4sysops.com/feed/'


class AProgrammerWithMicrosoftToolsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AProgrammerWithMicrosoftTools'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://msprogrammer.serviciipeweb.ro/feed/'


class AarononthewebParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Aaronontheweb'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.aaronstannard.com/syndication.axd'


class AllanSBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AllanSBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://sqlha.com/blog/feed/'


class AndyGibsonParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AndyGibson'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.andygibson.net/blog/feed/'


class AntonioSBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AntonioSBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://agoncal.wordpress.com/feed/'


class ArcaneCodeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ArcaneCode'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/ArcaneCode'


class AugustoAlvarezParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AugustoAlvarez'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/AugustoAlvarez'


class Channel9ParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Channel9'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://channel9.msdn.com/Feeds/RSS'


class CloudComputingBigDataHpcCodeinstinctParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CloudComputingBigDataHpcCodeinstinct'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.codeinstinct.pro/feeds/posts/default'


class ClusteringForMereMortalsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ClusteringForMereMortals'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://clusteringformeremortals.com/feed/'


class CommandLineFanaticParsingModule(SimpleRssBasicParsingModule):

    source_name = 'CommandLineFanatic'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://commandlinefanatic.com/rss.xml'


class DevcurryParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Devcurry'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.devcurry.com/feeds/posts/default/'


class DonTBeIffyParsingModule(SimpleRssBasicParsingModule):

    source_name = 'DonTBeIffy'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://thedatafarm.com/blog/feed/'


class ElegantCodeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ElegantCode'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/ElegantCode'


class FelipeOliveiraParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FelipeOliveira'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/GeeksAreTotallyIn'


class FromRavikanthSBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FromRavikanthSBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/RavikanthChaganti'


class FullFeedParsingModule(SimpleRssBasicParsingModule):

    source_name = 'FullFeed'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.addedbytes.com/added_bytes_full'


class GauravmantriComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'GauravmantriCom'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://gauravmantri.com/feed/'


class GeekSucksParsingModule(SimpleRssBasicParsingModule):

    source_name = 'GeekSucks'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/GeekSucks'


class GoodCodersCodeGreatReuseParsingModule(SimpleRssBasicParsingModule):

    source_name = 'GoodCodersCodeGreatReuse'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.catonmat.net/feed/'


class GunnarPeipmanSAspNetBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'GunnarPeipmanSAspNetBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/gunnarpeipman'


class HanselminutesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Hanselminutes'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/HanselminutesCompleteMP3'


class HelpDeskGeekHelpDeskTipsForItProsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HelpDeskGeekHelpDeskTipsForItPros'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feedproxy.google.com/ITHelpDeskGeek'


class HenrikOlssonSComputerSoftwareNotesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HenrikOlssonSComputerSoftwareNotes'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://holsson.wordpress.com/feed/'


class HongkiatComParsingModule(SimpleRssBasicParsingModule):

    source_name = 'HongkiatCom'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.hongkiat.com/blog/feed/'


class IcosmogeekParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Icosmogeek'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/cosmogeekinfo'


class InDepthFeaturesParsingModule(SimpleRssBasicParsingModule):

    source_name = 'InDepthFeatures'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://redmondmag.com/rss-feeds/in-depth.aspx'


class JenkovComNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'JenkovComNews'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds2.feedburner.com/jenkov-com?format=xml'


class JonathanGKoomeyPhDParsingModule(SimpleRssBasicParsingModule):

    source_name = 'JonathanGKoomeyPhD'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.koomey.com/rss'


class KScottAllenParsingModule(SimpleRssBasicParsingModule):

    source_name = 'KScottAllen'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/OdeToCode'


class MaartenBalliauwBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MaartenBalliauwBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds2.feedburner.com/maartenballiauw'


class MarceloSincicMvpParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MarceloSincicMvp'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://msincic.wordpress.com/feed/'


class MartinFowlerParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MartinFowler'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://martinfowler.com/feed.atom'


class MaxTrinidadThePowershellFrontParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MaxTrinidadThePowershellFront'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.maxtblog.com/rss'


class MethodOfFailedByTimHeuerParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MethodOfFailedByTimHeuer'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.timheuer.com/timheuer'


class MichaelCrumpParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MichaelCrump'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/MichaelCrump'


class NewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'News'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://mcpmag.com/rss-feeds/news.aspx'


class PetriItKnowledgebaseParsingModule(SimpleRssBasicParsingModule):

    source_name = 'PetriItKnowledgebase'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds2.feedburner.com/Petri'


class PrecisionComputingParsingModule(SimpleRssBasicParsingModule):

    source_name = 'PrecisionComputing'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.leeholmes.com/blog/feed/atom/'


class PublisherSRoundUpParsingModule(SimpleRssBasicParsingModule):

    source_name = 'PublisherSRoundUp'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://wmjasco.blogspot.com/feeds/posts/default'


class RandsInReposeParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RandsInRepose'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.randsinrepose.com/index.xml'


class RedmondReportParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RedmondReport'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://redmondmag.com/rss-feeds/redmond-report.aspx'


class RhyousParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Rhyous'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.rhyous.com/feed/'


class RichardSeroterSArchitectureMusingsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RichardSeroterSArchitectureMusings'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://seroter.wordpress.com/feed/'


class RickStrahlSWebLogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'RickStrahlSWebLog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feedproxy.google.com/rickstrahl'


class SdmSoftwareParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SdmSoftware'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.sdmsoftware.com/feed/'


class SecretgeekParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Secretgeek'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://secretgeek.net/rss.asp'


class ShawnWildermuthSBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ShawnWildermuthSBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/ShawnWildermuth'


class SimpleTalkRssFeedParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SimpleTalkRssFeed'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.simple-talk.com/feed/'


class SmashingMagazineFeedParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SmashingMagazineFeed'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://rss1.smashingmagazine.com/feed/'


class SteveSmithSBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'SteveSmithSBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.feedburner.com/StevenSmith'


class TechgenixNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TechgenixNews'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.techgenix.com/news/feed/'


class TecosystemsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Tecosystems'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://redmonk.com/sogrady/feed/rss/'


class TheArtOfSimplicityParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheArtOfSimplicity'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://bartwullems.blogspot.com/feeds/posts/default'


class TheExptaBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheExptaBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.expta.com/feeds/posts/default'


class TheMicrosoftPlatformParsingModule(SimpleRssBasicParsingModule):

    source_name = 'TheMicrosoftPlatform'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://microsoftplatform.blogspot.com/feeds/posts/default'


class ThinkingInSoftwareParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ThinkingInSoftware'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://thinkinginsoftware.blogspot.com/feeds/posts/default'


class VirtualisationManagementBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'VirtualisationManagementBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://virtualisationandmanagement.wordpress.com/feed/'


class VisioGuyParsingModule(SimpleRssBasicParsingModule):

    source_name = 'VisioGuy'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://www.visguy.com/feed/'


class WebcastsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Webcasts'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://redmondmag.com/rss-feeds/webcasts.aspx'


class WindowsPowershellBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'WindowsPowershellBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blogs.msdn.com/b/powershell/atom.aspx'


class WindowsServerDivisionWeblogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'WindowsServerDivisionWeblog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blogs.technet.com/b/windowsserver/rss.aspx'


class YouAreNotSoSmartParsingModule(SimpleRssBasicParsingModule):

    source_name = 'YouAreNotSoSmart'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://youarenotsosmart.com/feed/'


class YouVeBeenHaackedParsingModule(SimpleRssBasicParsingModule):

    source_name = 'YouVeBeenHaacked'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.haacked.com/haacked'


class AlexanderBindyuBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AlexanderBindyuBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blog.byndyu.ru/feeds/posts/default?alt=rss'


class ScottHanselmanSBlogParsingModule(SimpleRssBasicParsingModule):

    source_name = 'ScottHanselmanSBlog'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.hanselman.com/ScottHanselman'


class AndreyOnNetParsingModule(SimpleRssBasicParsingModule):

    source_name = 'AndreyOnNet'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://feeds.moveax.ru/devdotnet'


class MyInformationResourceBlogMirNetParsingModule(SimpleRssBasicParsingModule):

    source_name = 'MyInformationResourceBlogMirNet'
    projects = (
        os_friday_project,
    )
    rss_url = 'http://blog.mir.net/feeds/posts/default'


class EternalArrivalParsingModule(SimpleRssBasicParsingModule):

    source_name = 'EternalArrival'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://eternalarrival.com/feed/'


class Rss20TaggedMerkleTreesAndRelatedSimilarDataStructuresNotBusinessScamNewsParsingModule(SimpleRssBasicParsingModule):

    source_name = 'Rss20TaggedMerkleTreesAndRelatedSimilarDataStructuresNotBusinessScamNews'
    projects = (
        os_friday_project,
    )
    rss_url = 'https://lobste.rs/t/merkle-trees.rss'

