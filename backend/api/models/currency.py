"""Currency and Multi-Currency Support models."""
from django.db import models


class Currency(models.Model):
    """Currency model for multi-currency support."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='currencies',
        db_index=True,
    )

    code = models.CharField(max_length=3, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=1.0)
    is_base_currency = models.BooleanField(default=False)

    decimal_places = models.IntegerField(default=2)
    symbol_position = models.CharField(max_length=10, default='before')

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'currencies'
        verbose_name_plural = 'currencies'

    def __str__(self):
        return f"Currency(id={self.id}, code='{self.code}', name='{self.name}')"


class CurrencyExchangeRate(models.Model):
    """Currency exchange rate history."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='currency_exchange_rates',
        db_index=True,
    )

    from_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='exchange_rates_from',
    )
    to_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='exchange_rates_to',
    )

    rate = models.DecimalField(max_digits=15, decimal_places=6)
    effective_date = models.DateTimeField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='currency_exchange_rates_created',
    )

    class Meta:
        db_table = 'currency_exchange_rates'

    def __str__(self):
        return (
            f"CurrencyExchangeRate(id={self.id}, from={self.from_currency_id}, "
            f"to={self.to_currency_id}, rate={self.rate})"
        )


class TenantCurrency(models.Model):
    """Tenant currency settings."""

    tenant = models.OneToOneField(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='currency_settings',
        db_index=True,
    )

    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='tenant_base_settings',
    )

    allowed_currency_ids = models.TextField(null=True, blank=True)

    auto_update_rates = models.BooleanField(default=False)
    last_rate_update = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'tenant_currencies'

    def __str__(self):
        return (
            f"TenantCurrency(id={self.id}, tenant_id={self.tenant_id}, "
            f"base_currency_id={self.base_currency_id})"
        )
