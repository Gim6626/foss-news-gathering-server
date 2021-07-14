from django.db import migrations, models


def fill_digest_records_projects(apps, schema_editor):
    project_model = apps.get_model('gatherer', 'Project')
    dr_model = apps.get_model('gatherer', 'DigestRecord')
    fn_project = project_model.objects.get(name='FOSS News')
    for dr in dr_model.objects.all():
        if not dr.projects.all():
            dr.projects.set([fn_project])


class Migration(migrations.Migration):

    dependencies = [
        ('gatherer', '0022_removed_redundant_null_parameter_for_MtM_field'),
    ]

    operations = [
        migrations.RunPython(fill_digest_records_projects, migrations.RunPython.noop),
    ]
