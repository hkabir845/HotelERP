from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_public_booking_orders'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='uniq_recipe_ingredient',
            ),
        ),
        migrations.CreateModel(
            name='IngredientStockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(choices=[('receive', 'Receive'), ('deduct', 'Order deduction'), ('adjust', 'Adjustment'), ('waste', 'Waste')], max_length=20)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=10)),
                ('stock_before', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_after', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shortfall', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingredient_movements', to='api.user')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movements', to='api.ingredient')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_movements', to='api.order')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_movements', to='api.tenant')),
            ],
            options={
                'db_table': 'ingredient_stock_movements',
            },
        ),
    ]
