# Generated by Django 2.2.13 on 2021-07-14 04:03

import os
import yaml

from django.db import migrations, models
from gatherer.models import Keyword, DigestRecordSubcategory


def fill_keywords(apps, schema_editor):
    categories_keywords_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            'data',
                                            'digestrecordsubcategorykeywords.yaml')
    with open(categories_keywords_path, 'r') as fin:
        keywords = yaml.safe_load(fin)

    for category_name, keyword_types in keywords.items():
        for keyword_type, keywords_names in keyword_types.items():
            is_generic = keyword_type == 'generic'
            for keyword_name in keywords_names:
                category = DigestRecordSubcategory(category_name)
                keyword = Keyword(name=keyword_name, category=category.name, is_generic=is_generic)
                keyword.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0031_fixed_russian_name_for_project_name'),
    ]

    operations = [
        migrations.RunPython(fill_keywords, migrations.RunPython.noop),
    ]