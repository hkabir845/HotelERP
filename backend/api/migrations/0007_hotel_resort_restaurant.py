import json

from django.db import migrations


def add_restaurant_to_stay_properties(apps, schema_editor):
    Tenant = apps.get_model('api', 'Tenant')
    stay_types = ('hotel', 'resort', 'mixed')
    for tenant in Tenant.objects.filter(product_type__in=stay_types):
        raw = (tenant.enabled_modules or '').strip()
        try:
            modules = json.loads(raw) if raw else []
        except (TypeError, ValueError):
            modules = []
        if not isinstance(modules, list):
            modules = []
        changed = False
        if 'fnb' not in modules:
            modules.append('fnb')
            changed = True
        if 'recipes' not in modules:
            modules.append('recipes')
            changed = True
        if changed:
            tenant.enabled_modules = json.dumps(modules)
            tenant.save(update_fields=['enabled_modules'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_tenant_locale_settings'),
    ]

    operations = [
        migrations.RunPython(add_restaurant_to_stay_properties, noop),
    ]
