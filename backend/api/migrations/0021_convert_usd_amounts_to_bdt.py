from django.db import migrations


def convert_usd(apps, schema_editor):
    from api.money import convert_stored_usd_to_bdt

    convert_stored_usd_to_bdt(apps)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_remaining_screens'),
    ]

    operations = [
        migrations.RunPython(convert_usd, noop),
    ]
