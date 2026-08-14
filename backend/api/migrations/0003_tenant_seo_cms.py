from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_saas_tenant_modules'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='landing_template',
            field=models.CharField(blank=True, default='default', max_length=50),
        ),
        migrations.AddField(
            model_name='tenant',
            name='landing_content',
            field=models.TextField(blank=True, default='{}'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='seo_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tenant',
            name='seo_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tenant',
            name='seo_keywords',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='tenant',
            name='og_image',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
