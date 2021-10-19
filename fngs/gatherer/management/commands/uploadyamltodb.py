from django.core.management.base import BaseCommand
from gatherer.models import DigestRecord
import yaml
import datetime
from pprint import pprint


SUBCATEGORY_MAPPING = {
    'Мероприятия': 'EVENTS',
    'Внедрения': 'INTROS',
    'Открытие кода и данных': 'OPENING',
    'Новости FOSS организаций': 'NEWS',
    'DIY': 'DIY',
    'Юридические вопросы': 'LAW',
    'Ядро и дистрибутивы': 'KnD',
    'Системное': 'SYSTEM',
    'Специальное': 'SPECIAL',
    'Менеджмент': 'MANAGEMENT',
    'Пользовательское': 'USER',
    'Железо': 'HARDWARE',
    'Системный софт': 'SYSTEM',
    'Безопасность': 'SECURITY',
    'DevOps': 'DEVOPS',
    'Data Science': 'DATA_SCIENCE',
    'Web': 'WEB',
    'Для разработчиков': 'DEV',
    'Специальный софт': 'SPECIAL',
    'Мультимедиа': 'MULTIMEDIA',
    'Игры': 'GAMES',
    'Пользовательский софт': 'USER',
    'Разное': 'MISC',
}


class Command(BaseCommand):
    help = 'Upload YAML to database'

    def add_arguments(self, parser):
        parser.add_argument('YAML_FILE',
                            type=str,
                            help='YAML file with digest records')

    def handle(self, *args, **options):
        fin = open(options['YAML_FILE'], 'r')
        fin_data = yaml.safe_load(fin)
        for record_dict in fin_data:
            category = record_dict['content_type']
            dt = datetime.datetime.strptime(record_dict['datetime'], '%Y-%m-%d %H:%M:%S %z')
            digest_number = record_dict['digest_number']
            state = record_dict['state']
            content_category = record_dict['content_category']
            title = record_dict['title']
            url = record_dict['url']
            is_main = False
            if category == 'main':
                category = 'news'
                is_main = True
            state = state.upper()
            category = category.upper()
            if content_category in SUBCATEGORY_MAPPING:
                content_category = SUBCATEGORY_MAPPING[content_category]
            digest_record = DigestRecord(dt=dt,
                                         title=title,
                                         url=url,
                                         state=state,
                                         digest_number=digest_number,
                                         is_main=is_main,
                                         category=category,
                                         subcategory=content_category)

            same_in_db = DigestRecord.objects.filter(url=url)
            if same_in_db:
                print(f'Ignored "{digest_record}" as such URL already exists in database')
            else:
                digest_record.save()
