from django.db import models


class DigestRecord(models.Model):
    dt = models.DateTimeField(verbose_name='Date&time')
    title = models.CharField(verbose_name='Title', max_length=256, unique=True, blank=False)
    url = models.CharField(verbose_name='URL', max_length=256, unique=True, blank=False)

    class Meta:
        verbose_name = 'Digest Record'
        verbose_name_plural = 'Digest Records'

    def __str__(self):
        return f'{self.dt} {self.title} {self.url}'
