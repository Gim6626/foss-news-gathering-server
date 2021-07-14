from django.db import migrations
from gatherer.models import Language

RUSSIAN_SOURCES = (
    'habr.com',
    'opennet.ru',
    'cnews.ru',
    'vk.com',
    'pingvinus.ru',
    'losst.ru',
    'linux.org.ru',
    'youtube.com',  # Confusing, yes, but currently we use videos from only one blogger and he is russian
    'basealt.ru',
    'weeklyosm.eu/ru',
    'ixbt.com',
    '3dnews.ru',
    'ruops.medium.com',
    'evrone.ru',
    'tadviser.ru',
    'it-world.ru',
    'astralinux.ru',
    'ferra.ru',
    'rbc.ru',
    'dev.by',
)


def fill_digest_records_languages(apps, schema_editor):
    dr_model = apps.get_model('gatherer', 'DigestRecord')
    for dr in dr_model.objects.all():
        for s in RUSSIAN_SOURCES:
            if s in dr.url:
                dr.language = Language.RUSSIAN.name
                break
            else:
                dr.language = Language.ENGLISH.name
        dr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0024_fix_few_fields_length'),
    ]

    operations = [
        migrations.RunPython(fill_digest_records_languages, migrations.RunPython.noop),
    ]

