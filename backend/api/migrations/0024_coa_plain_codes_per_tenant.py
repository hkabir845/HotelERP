# Generated manually — FSERP-style plain account codes (no tenant prefix).

from django.db import migrations, models


def strip_tenant_prefix_from_codes(apps, schema_editor):
    """Convert codes like '1-1110' → '1110' (FSERP style)."""
    ChartOfAccount = apps.get_model('api', 'ChartOfAccount')
    for row in ChartOfAccount.objects.all().iterator():
        code = (row.account_code or '').strip()
        if '-' not in code:
            continue
        # Only strip leading numeric tenant-id prefix: "12-1110" → "1110"
        left, right = code.split('-', 1)
        if not left.isdigit() or not right:
            continue
        plain = right
        # Skip if this tenant already has the plain code on another row
        clash = (
            ChartOfAccount.objects.filter(tenant_id=row.tenant_id, account_code=plain)
            .exclude(pk=row.pk)
            .exists()
        )
        if clash:
            continue
        row.account_code = plain
        row.save(update_fields=['account_code'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_loan_interest_bearing_individual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartofaccount',
            name='account_code',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='chartofaccount',
            unique_together={('tenant', 'account_code')},
        ),
        migrations.AddIndex(
            model_name='chartofaccount',
            index=models.Index(fields=['tenant', 'account_code'], name='chart_of_ac_tenant__7a2b1c_idx'),
        ),
        migrations.RunPython(strip_tenant_prefix_from_codes, noop_reverse),
    ]
