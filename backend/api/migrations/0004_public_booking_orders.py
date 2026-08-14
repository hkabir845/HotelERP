from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_tenant_seo_cms'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='requested_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Guest-requested serve/delivery time',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.CharField(db_index=True, max_length=20),
        ),
        migrations.AddConstraint(
            model_name='table',
            constraint=models.UniqueConstraint(
                fields=('tenant', 'table_number'),
                name='uniq_table_per_tenant',
            ),
        ),
    ]
