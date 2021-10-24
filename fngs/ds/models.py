from django.db import models

from gatherer.models import DigestRecord


class Lemma(models.Model):

    text = models.CharField(verbose_name='Text',
                            max_length=2048,
                            blank=False,
                            null=False,
                            unique=True)

    def __str__(self):
        return self.text


class DigestRecordLemma(models.Model):

    digest_record = models.ForeignKey(to=DigestRecord,
                                      on_delete=models.PROTECT,
                                      blank=False,
                                      null=False)
    lemma = models.ForeignKey(to=Lemma,
                              on_delete=models.PROTECT,
                              blank=False,
                              null=False)
    count = models.IntegerField(verbose_name='Count',
                                null=False,
                                blank=False,
                                default=0)

    class Meta:
        unique_together = (
            'digest_record',
            'lemma',
        )
