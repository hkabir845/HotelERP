from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_recipe_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='currency',
            field=models.CharField(default='BDT', max_length=8),
        ),
        migrations.AddField(
            model_name='tenant',
            name='timezone',
            field=models.CharField(default='Asia/Dhaka', max_length=64),
        ),
        migrations.AddField(
            model_name='tenant',
            name='date_format',
            field=models.CharField(default='DD/MM/YYYY', max_length=20),
        ),
        migrations.AddField(
            model_name='tenant',
            name='time_format',
            field=models.CharField(default='12h', max_length=8),
        ),
    ]
