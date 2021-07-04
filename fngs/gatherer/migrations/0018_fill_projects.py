from django.db import migrations, models


def fill_projects(apps, schema_editor):
    project_model = apps.get_model('gatherer', 'Project')
    basic_projects_names = ('FOSS News', 'OS Friday')
    for basic_project_name in basic_projects_names:
        if not project_model.objects.filter(name=basic_project_name):
            new_basic_project = project_model(name=basic_project_name)
            new_basic_project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0017_add_project_model'),
    ]

    operations = [
        migrations.RunPython(fill_projects, migrations.RunPython.noop),
    ]
