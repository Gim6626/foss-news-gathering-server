from django.db import models
from enum import Enum


class DigestRecordState(Enum):
    UNKNOWN = 'unknown'
    IN_DIGEST = 'in_digest'
    OUTDATED = 'outdated'
    IGNORED = 'ignored'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class DigestRecordCategory(Enum):
    UNKNOWN = 'unknown'
    NEWS = 'news'
    ARTICLES = 'articles'
    RELEASES = 'releases'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class DigestRecordSubcategory(Enum):
    EVENTS = 'events'
    INTROS = 'intros'
    OPENING = 'opening'
    NEWS = 'news'
    DIY = 'diy'
    LAW = 'law'
    KnD = 'knd'
    SYSTEM = 'system'
    SPECIAL = 'special'
    EDUCATION = 'education'
    DATABASES = 'db'
    MULTIMEDIA = 'multimedia'
    MOBILE = 'mobile'
    SECURITY = 'security'
    SYSADM = 'sysadm'
    DEVOPS = 'devops'
    DATA_SCIENCE = 'data_science'
    WEB = 'web'
    DEV = 'dev'
    TESTING = 'testing'
    HISTORY = 'history'
    MANAGEMENT = 'management'
    USER = 'user'
    GAMES = 'games'
    HARDWARE = 'hardware'
    MISC = 'misc'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class DigestRecord(models.Model):
    dt = models.DateTimeField(verbose_name='Date&time',
                              null=True,
                              blank=True)
    gather_dt = models.DateTimeField(verbose_name='Gather Date&time',
                                     null=True,
                                     blank=True)
    title = models.CharField(verbose_name='Title',
                             max_length=256,
                             blank=False)
    url = models.CharField(verbose_name='URL',
                           max_length=256,
                           unique=True,
                           blank=False)
    state = models.CharField(verbose_name='State',
                             choices=DigestRecordState.choices(),
                             max_length=256,
                             null=True,
                             blank=True)
    digest_number = models.IntegerField(verbose_name='Digest Number',
                                        null=True,
                                        blank=True)
    is_main = models.BooleanField(verbose_name='Is main post',
                                  null=True,
                                  blank=True)
    category = models.CharField(verbose_name='Category',
                                choices=DigestRecordCategory.choices(),
                                max_length=256,
                                null=True,
                                blank=True)
    subcategory = models.CharField(verbose_name='Subcategory',
                                   choices=DigestRecordSubcategory.choices(),
                                   max_length=256,
                                   null=True,
                                   blank=True)
    keywords = models.CharField(verbose_name='Keywords',
                                max_length=1024,
                                null=True,
                                blank=True)
    projects = models.ManyToManyField(to='Project',
                                      verbose_name='Projects',
                                      related_name='records')

    def projects_names(self):
        return f'{", ".join([p.name for p in self.projects.all()])}'

    class Meta:
        verbose_name = 'Digest Record'
        verbose_name_plural = 'Digest Records'

    def __str__(self):
        return f'{self.dt} {self.title} {self.url} #{self.digest_number} state:"{self.state}" cat:"{self.category}" subcat: "{self.subcategory}" keywords: "{self.keywords}"'


class DigestRecordDuplicate(models.Model):

    digest_number = models.IntegerField(verbose_name='Digest Number',
                                        null=True,
                                        blank=True)
    digest_records = models.ManyToManyField(to=DigestRecord,
                                            verbose_name='Digest Record',
                                            related_name='duplicates',
                                            )

    def digest_records_titles(self):
        return f'{", ".join([dr.title for dr in self.digest_records.all()])}'

    def __str__(self):
        return self.digest_records_titles()


class Project(models.Model):

    name = models.CharField(verbose_name='Название', max_length=64)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name
