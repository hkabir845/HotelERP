from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_hotel_resort_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='source',
            field=models.CharField(db_index=True, default='pos', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='guest_kind',
            field=models.CharField(db_index=True, default='walk_in', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(db_index=True, default='unpaid', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='checkout_ref',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True),
        ),
    ]
