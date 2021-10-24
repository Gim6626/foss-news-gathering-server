from django.db import migrations
from django.db.models.functions import Length

from gatherer.models import *
from ds.models import *

import lemminflect
import nltk
import re
import math


def fill_lemmas_and_connections_to_digest_records(apps, schema_editor):
    all_valued_records = DigestRecord.objects.filter(language=Language.ENGLISH.name)
    one_percent_count = math.ceil(all_valued_records.count() / 100)
    last_printed_percent = None
    for dr_i, dr in enumerate(all_valued_records):
        s = dr.title
        if dr.cleared_description:
            s += ' ' + dr.cleared_description
        words = nltk.word_tokenize(s)
        word_lemmas_counts = {}
        for word in words:
            word_lemmas = lemminflect.getAllLemmas(word)
            lemmas_keys = ('NOUN', 'VERB', 'AUX', 'ADV', 'ADJ')
            word_lemmas_plain = []
            for lk in lemmas_keys:
                if lk in word_lemmas:
                    word_lemmas_plain += (l.lower() for l in word_lemmas[lk])
            if not word_lemmas and re.match(r'\w', word):
                word_lemmas_plain.append(word.lower())
            for l in word_lemmas_plain:
                if l not in word_lemmas_counts:
                    word_lemmas_counts[l] = 1
                else:
                    word_lemmas_counts[l] += 1
        for lemma_text, lemma_count_in_dr in word_lemmas_counts.items():
            existing_lemmas = Lemma.objects.filter(text=lemma_text)
            if not existing_lemmas:
                lemma_object = Lemma(text=lemma_text)
                lemma_object.save()
            else:
                lemma_object = existing_lemmas[0]
            existing_digest_record_lemmas = DigestRecordLemma.objects.filter(lemma=lemma_object, digest_record=dr)
            if not existing_digest_record_lemmas:
                digest_record_lemma = DigestRecordLemma(lemma=lemma_object, digest_record=dr, count=lemma_count_in_dr)
                digest_record_lemma.save()

        if (dr_i + 1) % one_percent_count == 0:
            current_percent = math.ceil((dr_i + 1) / one_percent_count)
            if last_printed_percent is None or current_percent != last_printed_percent:
                last_printed_percent = current_percent
                print(f'Processed {current_percent}% ({dr_i + 1} records, {all_valued_records.count()} total, {all_valued_records.count() - dr_i - 1} left)')


class Migration(migrations.Migration):

    dependencies = [
        ('ds', '0004_increase_lemma_max_length'),
    ]

    operations = [
        migrations.RunPython(fill_lemmas_and_connections_to_digest_records, migrations.RunPython.noop),
    ]
