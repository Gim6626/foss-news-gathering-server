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
from .logger import logger, init_logger


SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

parsing_modules_names = []
days_count = None
keywords = {}


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
            posts_data_one = self._parse(parsing_module)
            self._save_to_database(posts_data_one)
        logger.info(f'Finished parsing all sources, all saved to database')  # TODO: Add stats

    def _parse(self, parsing_module):
        logger.info(f'Started parsing {parsing_module.source_name}')
        posts_data = parsing_module.parse(days_count)
        posts_data_one = PostsData(parsing_module.source_name,
                                   parsing_module.projects,
                                   posts_data,
                                   parsing_module.language,
                                   parsing_module.warning)
        for post_data in posts_data_one.posts_data_list:
            logger.info(f'New post {post_data.dt if post_data.dt is not None else "?"} "{post_data.title}" {post_data.url}')
        logger.debug(f'Parsed from {parsing_module.source_name}: {[(post_data.title, post_data.url) for post_data in posts_data_one.posts_data_list]}')
        logger.info(f'Finished parsing {parsing_module.source_name}, got {len(posts_data_one.posts_data_list)} post(s)')
        return posts_data_one

    def _save_to_database(self, posts_data_one: PostsData):
        logger.info(f'Saving to database for source "{posts_data_one.source_name}"')
        added_digest_records_count = 0
        already_existing_digest_records_count = 0
        for post_data in posts_data_one.posts_data_list:
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
                                             state=DigestRecordState.UNKNOWN.name
                                                   if not post_data.filtered
                                                   else DigestRecordState.FILTERED.name,
                                             keywords=';'.join(post_data.keywords),
                                             language=posts_data_one.language.name)
                digest_record.save()
                digest_record.projects.set(posts_data_one.projects)
                digest_record.save()
                added_digest_records_count += 1
                logger.debug(f'Added {short_post_data_str} to database')
        logger.info(f'Finished saving to database for source "{posts_data_one.source_name}", added {added_digest_records_count} digest record(s), {already_existing_digest_records_count} already existed')

    def _init_globals(self, **options):
        init_logger(options['debug'])
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
    # My
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
    # From Alex
    OPEN_SOURCE_ON_REDDIT = OpenSourceOnRedditParsingModule.source_name
    LINUX_GNU_LINUX_FREE_SOFTWARE = LinuxGnuLinuxFreeSoftwareParsingModule.source_name
    CONTAINER_JOURNAL = ContainerJournalParsingModule.source_name
    BLOG_CLOUD_NATIVE_COMPUTING_FOUNDATION = BlogCloudNativeComputingFoundationParsingModule.source_name
    KUBEDEX_COM = KubedexComParsingModule.source_name
    CILIUM_BLOG = CiliumBlogParsingModule.source_name
    ENGINEERING_DOCKER_BLOG = EngineeringDockerBlogParsingModule.source_name
    BLOG_SYSDIG = BlogSysdigParsingModule.source_name
    CODEFRESH = CodefreshParsingModule.source_name
    AQUA_BLOG = AquaBlogParsingModule.source_name
    AMBASSADOR_API_GATEWAY = AmbassadorApiGatewayParsingModule.source_name
    WEAVEWORKS = WeaveworksParsingModule.source_name
    KUBEWEEKLY_ARCHIVE_FEED = KubeweeklyArchiveFeedParsingModule.source_name
    LACHLAN_EVENSON = LachlanEvensonParsingModule.source_name
    SOFTWARE_DEFINED_TALK = SoftwareDefinedTalkParsingModule.source_name
    PROMETHEUS_BLOG = PrometheusBlogParsingModule.source_name
    SYSDIG = SysdigParsingModule.source_name
    INNOVATE_EVERYWHERE_ON_RANCHER_LABS = InnovateEverywhereOnRancherLabsParsingModule.source_name
    THE_NEW_STACK_PODCAST = TheNewStackPodcastParsingModule.source_name
    KUBERNETES_ON_MEDIUM = KubernetesOnMediumParsingModule.source_name
    RAMBLINGS_FROM_JESSIE = RamblingsFromJessieParsingModule.source_name
    DISCUSS_KUBERNETES_LATEST_TOPICS = DiscussKubernetesLatestTopicsParsingModule.source_name
    PROJECT_CALICO = ProjectCalicoParsingModule.source_name
    LAST_WEEK_IN_KUBERNETES_DEVELOPMENT = LastWeekInKubernetesDevelopmentParsingModule.source_name
    KUBERNETES = KubernetesParsingModule.source_name
    ENVOY_PROXY = EnvoyProxyParsingModule.source_name
    THE_NEW_STACK_ANALYSTS = TheNewStackAnalystsParsingModule.source_name
    TIGERA = TigeraParsingModule.source_name
    TWISTLOCK = TwistlockParsingModule.source_name
    BLOG_ON_RANCHER_LABS = BlogOnRancherLabsParsingModule.source_name
    THE_NEW_STACK = TheNewStackParsingModule.source_name
    KONGHQ = KonghqParsingModule.source_name
    DOCKER_ON_MEDIUM = DockerOnMediumParsingModule.source_name
    DOCKER_BLOG = DockerBlogParsingModule.source_name
    DISCUSS_KUBERNETES_LATEST_POSTS = DiscussKubernetesLatestPostsParsingModule.source_name
    D2_IQ_BLOG = D2IqBlogParsingModule.source_name
    PODCTL_ENTERPRISE_KUBERNETES = PodctlEnterpriseKubernetesParsingModule.source_name
    ISTIO_BLOG_AND_NEWS = IstioBlogAndNewsParsingModule.source_name
    PROGRAMMING_KUBERNETES = ProgrammingKubernetesParsingModule.source_name
    KUBERNETES_PODCAST_FROM_GOOGLE = KubernetesPodcastFromGoogleParsingModule.source_name
    CLOUD_NATIVE_COMPUTING_FOUNDATION = CloudNativeComputingFoundationParsingModule.source_name
    BLOG_ON_STACKROX_SECURITY_BUILT_IN = BlogOnStackroxSecurityBuiltInParsingModule.source_name
    RECENT_QUESTIONS_OPEN_SOURCE_STACK_EXCHANGE = RecentQuestionsOpenSourceStackExchangeParsingModule.source_name
    LXER_LINUX_NEWS = LxerLinuxNewsParsingModule.source_name
    NATIVECLOUD_DEV = NativecloudDevParsingModule.source_name
    LINUXLINKS = LinuxlinksParsingModule.source_name
    LOBSTERS_JAVA_JAVA_PROGRAMMING = LobstersJavaJavaProgrammingParsingModule.source_name
    FLOSS_WEEKLY_VIDEO = FlossWeeklyVideoParsingModule.source_name
    LOBSTERS_NODEJS_NODE_JS_PROGRAMMING = LobstersNodejsNodeJsProgrammingParsingModule.source_name
    OPEN_SOURCE_ON_MEDIUM = OpenSourceOnMediumParsingModule.source_name
    BLOG_ON_SMALLSTEP = BlogOnSmallstepParsingModule.source_name
    LINUX_NOTES_FROM_DARKDUCK = LinuxNotesFromDarkduckParsingModule.source_name
    MICROSOFT_OPEN_SOURCE_STORIES = MicrosoftOpenSourceStoriesParsingModule.source_name
    LOBSTERS_UNIX_NIX = LobstersUnixNixParsingModule.source_name
    AMERICAN_EXPRESS_TECHNOLOGY = AmericanExpressTechnologyParsingModule.source_name
    NEWEST_OPEN_SOURCE_QUESTIONS_FEED = NewestOpenSourceQuestionsFeedParsingModule.source_name
    TEEJEETECH = TeejeetechParsingModule.source_name
    FREEDOM_PENGUIN = FreedomPenguinParsingModule.source_name
    LOBSTERS_LINUX_LINUX = LobstersLinuxLinuxParsingModule.source_name
    CRUNCH_TOOLS = CrunchToolsParsingModule.source_name
    LINUX_UPRISING_BLOG = LinuxUprisingBlogParsingModule.source_name
    EAGLEMAN_BLOG = EaglemanBlogParsingModule.source_name
    DBAKEVLAR = DbakevlarParsingModule.source_name
    ENGBLOG_RU = EngblogRuParsingModule.source_name
    LOBSTERS_DOTNET_C_F_NET_PROGRAMMING = LobstersDotnetCFNetProgrammingParsingModule.source_name
    LOBSTERS_WEB_WEB_DEVELOPMENT_AND_NEWS = LobstersWebWebDevelopmentAndNewsParsingModule.source_name
    MORNING_DEW_BY_ALVIN_ASHCRAFT = MorningDewByAlvinAshcraftParsingModule.source_name
    LOBSTERS_SECURITY_NETSEC_APPSEC_AND_INFOSEC = LobstersSecurityNetsecAppsecAndInfosecParsingModule.source_name
    BLOG = BlogParsingModule.source_name
    LOBSTERS_DISTRIBUTED_DISTRIBUTED_SYSTEMS = LobstersDistributedDistributedSystemsParsingModule.source_name
    LOBSTERS_DEVOPS_DEVOPS = LobstersDevopsDevopsParsingModule.source_name
    RSS = RssParsingModule.source_name
    AZURE_ADVOCATES_CONTENT_WRAP_UP = AzureAdvocatesContentWrapUpParsingModule.source_name
    FLANT_BLOG = FlantBlogParsingModule.source_name
    THOUGHTWORKS_INSIGHTS = ThoughtworksInsightsParsingModule.source_name
    LOBSTERS_OSDEV_OPERATING_SYSTEM_DESIGN_AND_DEVELOPMENT_WHEN_NO_SPECIFIC_OS_TAG_EXISTS = LobstersOsdevOperatingSystemDesignAndDevelopmentWhenNoSpecificOsTagExistsParsingModule.source_name
    MICROSOFT_DEVRADIO = MicrosoftDevradioParsingModule.source_name
    NEW_BLOG_ARTICLES_IN_MICROSOFT_TECH_COMMUNITY = NewBlogArticlesInMicrosoftTechCommunityParsingModule.source_name
    FOSSLIFE = FosslifeParsingModule.source_name
    AZURE_INFOHUB_RSS_AZURE = AzureInfohubRssAzureParsingModule.source_name
    PERFORMANCE_IS_A_FEATURE = PerformanceIsAFeatureParsingModule.source_name
    LOBSTERS_WASM_WEBASSEMBLY = LobstersWasmWebassemblyParsingModule.source_name
    THE_COMMUNITY_ROUNDTABLE = TheCommunityRoundtableParsingModule.source_name
    RSS20_TAGGED_MOBILE_MOBILE_APP_WEB_DEVELOPMENT = Rss20TaggedMobileMobileAppWebDevelopmentParsingModule.source_name
    AWS_ARCHITECTURE_BLOG = AwsArchitectureBlogParsingModule.source_name
    HEPTIO_UPLOADS_ON_YOUTUBE = HeptioUploadsOnYoutubeParsingModule.source_name
    ALEX_ELLIS_OPENFAAS_COMMUNITY_AWESOMENESS_ON_YOUTUBE = AlexEllisOpenfaasCommunityAwesomenessOnYoutubeParsingModule.source_name
    VMWARE_CLOUD_NATIVE_APPS_UPLOADS_ON_YOUTUBE = VmwareCloudNativeAppsUploadsOnYoutubeParsingModule.source_name
    D2_IQ = D2IqParsingModule.source_name
    TIGERA_UPLOADS_ON_YOUTUBE = TigeraUploadsOnYoutubeParsingModule.source_name
    CNCF_CLOUD_NATIVE_COMPUTING_FOUNDATION_UPLOADS_ON_YOUTUBE = CncfCloudNativeComputingFoundationUploadsOnYoutubeParsingModule.source_name
    CEPH_UPLOADS_ON_YOUTUBE = CephUploadsOnYoutubeParsingModule.source_name
    ROOK_ROOK_PRESENTATIONS_ON_YOUTUBE = RookRookPresentationsOnYoutubeParsingModule.source_name
    DOCKER = DockerParsingModule.source_name
    ROOK_UPLOADS_ON_YOUTUBE = RookUploadsOnYoutubeParsingModule.source_name
    CNCF_CLOUD_NATIVE_COMPUTING_FOUNDATION = CncfCloudNativeComputingFoundationParsingModule.source_name
    WEAVEWORKS_INC_WEAVE_ONLINE_USER_GROUPS_ON_YOUTUBE = WeaveworksIncWeaveOnlineUserGroupsOnYoutubeParsingModule.source_name
    KUBERNAUTS_IO_UPLOADS_ON_YOUTUBE = KubernautsIoUploadsOnYoutubeParsingModule.source_name
    ALEX_ELLIS_UPLOADS_ON_YOUTUBE = AlexEllisUploadsOnYoutubeParsingModule.source_name
    CEPH_CEPH_TESTING_WEEKLY_ON_YOUTUBE = CephCephTestingWeeklyOnYoutubeParsingModule.source_name
    NET_CURRY_RECENT_ARTICLES = NetCurryRecentArticlesParsingModule.source_name
    THREE_HUNDRED_SIXTY_DEGREE_DB_PROGRAMMING = ThreeHundredSixtyDegreeDbProgrammingParsingModule.source_name
    FOUR_SYSOPS = FourSysopsParsingModule.source_name
    A_PROGRAMMER_WITH_MICROSOFT_TOOLS = AProgrammerWithMicrosoftToolsParsingModule.source_name
    AARONONTHEWEB = AarononthewebParsingModule.source_name
    ALLAN_S_BLOG = AllanSBlogParsingModule.source_name
    ANDY_GIBSON = AndyGibsonParsingModule.source_name
    ANTONIO_S_BLOG = AntonioSBlogParsingModule.source_name
    ARCANE_CODE = ArcaneCodeParsingModule.source_name
    AUGUSTO_ALVAREZ = AugustoAlvarezParsingModule.source_name
    CHANNEL9 = Channel9ParsingModule.source_name
    CLOUD_COMPUTING_BIG_DATA_HPC_CODEINSTINCT = CloudComputingBigDataHpcCodeinstinctParsingModule.source_name
    CLUSTERING_FOR_MERE_MORTALS = ClusteringForMereMortalsParsingModule.source_name
    COMMAND_LINE_FANATIC = CommandLineFanaticParsingModule.source_name
    DEVCURRY = DevcurryParsingModule.source_name
    DON_T_BE_IFFY = DonTBeIffyParsingModule.source_name
    ELEGANT_CODE = ElegantCodeParsingModule.source_name
    FELIPE_OLIVEIRA = FelipeOliveiraParsingModule.source_name
    FROM_RAVIKANTH_S_BLOG = FromRavikanthSBlogParsingModule.source_name
    FULL_FEED = FullFeedParsingModule.source_name
    GAURAVMANTRI_COM = GauravmantriComParsingModule.source_name
    GEEK_SUCKS = GeekSucksParsingModule.source_name
    GOOD_CODERS_CODE_GREAT_REUSE = GoodCodersCodeGreatReuseParsingModule.source_name
    GUNNAR_PEIPMAN_S_ASP_NET_BLOG = GunnarPeipmanSAspNetBlogParsingModule.source_name
    HANSELMINUTES = HanselminutesParsingModule.source_name
    HELP_DESK_GEEK_HELP_DESK_TIPS_FOR_IT_PROS = HelpDeskGeekHelpDeskTipsForItProsParsingModule.source_name
    HENRIK_OLSSON_S_COMPUTER_SOFTWARE_NOTES = HenrikOlssonSComputerSoftwareNotesParsingModule.source_name
    HONGKIAT_COM = HongkiatComParsingModule.source_name
    ICOSMOGEEK = IcosmogeekParsingModule.source_name
    IN_DEPTH_FEATURES = InDepthFeaturesParsingModule.source_name
    JENKOV_COM_NEWS = JenkovComNewsParsingModule.source_name
    JONATHAN_G_KOOMEY_PH_D = JonathanGKoomeyPhDParsingModule.source_name
    K_SCOTT_ALLEN = KScottAllenParsingModule.source_name
    MAARTEN_BALLIAUW_BLOG = MaartenBalliauwBlogParsingModule.source_name
    MARCELO_SINCIC_MVP = MarceloSincicMvpParsingModule.source_name
    MARTIN_FOWLER = MartinFowlerParsingModule.source_name
    MAX_TRINIDAD_THE_POWERSHELL_FRONT = MaxTrinidadThePowershellFrontParsingModule.source_name
    METHOD_OF_FAILED_BY_TIM_HEUER = MethodOfFailedByTimHeuerParsingModule.source_name
    MICHAEL_CRUMP = MichaelCrumpParsingModule.source_name
    NEWS = NewsParsingModule.source_name
    PETRI_IT_KNOWLEDGEBASE = PetriItKnowledgebaseParsingModule.source_name
    PRECISION_COMPUTING = PrecisionComputingParsingModule.source_name
    PUBLISHER_S_ROUND_UP = PublisherSRoundUpParsingModule.source_name
    RANDS_IN_REPOSE = RandsInReposeParsingModule.source_name
    REDMOND_REPORT = RedmondReportParsingModule.source_name
    RHYOUS = RhyousParsingModule.source_name
    RICHARD_SEROTER_S_ARCHITECTURE_MUSINGS = RichardSeroterSArchitectureMusingsParsingModule.source_name
    RICK_STRAHL_S_WEB_LOG = RickStrahlSWebLogParsingModule.source_name
    SDM_SOFTWARE = SdmSoftwareParsingModule.source_name
    SECRETGEEK = SecretgeekParsingModule.source_name
    SHAWN_WILDERMUTH_S_BLOG = ShawnWildermuthSBlogParsingModule.source_name
    SIMPLE_TALK_RSS_FEED = SimpleTalkRssFeedParsingModule.source_name
    SMASHING_MAGAZINE_FEED = SmashingMagazineFeedParsingModule.source_name
    STEVE_SMITH_S_BLOG = SteveSmithSBlogParsingModule.source_name
    TECHGENIX_NEWS = TechgenixNewsParsingModule.source_name
    TECOSYSTEMS = TecosystemsParsingModule.source_name
    THE_ART_OF_SIMPLICITY = TheArtOfSimplicityParsingModule.source_name
    THE_EXPTA_BLOG = TheExptaBlogParsingModule.source_name
    THE_MICROSOFT_PLATFORM = TheMicrosoftPlatformParsingModule.source_name
    THINKING_IN_SOFTWARE = ThinkingInSoftwareParsingModule.source_name
    VIRTUALISATION_MANAGEMENT_BLOG = VirtualisationManagementBlogParsingModule.source_name
    VISIO_GUY = VisioGuyParsingModule.source_name
    WEBCASTS = WebcastsParsingModule.source_name
    WINDOWS_POWERSHELL_BLOG = WindowsPowershellBlogParsingModule.source_name
    WINDOWS_SERVER_DIVISION_WEBLOG = WindowsServerDivisionWeblogParsingModule.source_name
    YOU_ARE_NOT_SO_SMART = YouAreNotSoSmartParsingModule.source_name
    YOU_VE_BEEN_HAACKED = YouVeBeenHaackedParsingModule.source_name
    ALEXANDER_BINDYU_BLOG = AlexanderBindyuBlogParsingModule.source_name
    SCOTT_HANSELMAN_S_BLOG = ScottHanselmanSBlogParsingModule.source_name
    ANDREY_ON_NET = AndreyOnNetParsingModule.source_name
    MY_INFORMATION_RESOURCE_BLOG_MIR_NET = MyInformationResourceBlogMirNetParsingModule.source_name
    ETERNAL_ARRIVAL = EternalArrivalParsingModule.source_name
    RSS20_TAGGED_MERKLE_TREES_AND_RELATED_SIMILAR_DATA_STRUCTURES_NOT_BUSINESS_SCAM_NEWS = Rss20TaggedMerkleTreesAndRelatedSimilarDataStructuresNotBusinessScamNewsParsingModule.source_name


PARSING_MODULES_TYPES = tuple((t.value for t in ParsingModuleType))
