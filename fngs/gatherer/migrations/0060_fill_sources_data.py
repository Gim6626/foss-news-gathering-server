# Generated by Django 2.2.13 on 2021-07-14 04:03

import os
import yaml

from django.db import migrations, models
from gatherer.models import (
    DigestRecordsSource,
    Project,
)


def fill_sources_data(apps, schema_editor):
    parsing_modules_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                             'data',
                                             'parsing_modules_data.yaml')
    with open(parsing_modules_data_path, 'r') as fin:
        parsing_modules_data = yaml.safe_load(fin)
    for parsing_module_name, parsing_module_data in parsing_modules_data.items():
        source = DigestRecordsSource.objects.get(name=parsing_module_name)
        source.data_url = parsing_module_data['data_url']
        source.language = parsing_module_data['language']
        projects = []
        for parsing_module_project_name in parsing_module_data['projects']:
            project = Project.objects.get(name=parsing_module_project_name)
            projects.append(project)
        source.projects.set(projects)
        source.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0059_add_more_source_fields'),
    ]

    operations = [
        migrations.RunPython(fill_sources_data, migrations.RunPython.noop),
    ]
