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
    DEVOPS = 'devops'
    DATA_SCIENCE = 'data_science'
    WEB = 'web'
    DEV = 'dev'
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

    class Meta:
        verbose_name = 'Digest Record'
        verbose_name_plural = 'Digest Records'

    def __str__(self):
        return f'{self.dt} {self.title} {self.url} #{self.digest_number} state:"{self.state}" cat:"{self.category}" subcat: "{self.subcategory}"'
