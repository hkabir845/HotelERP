"""BDT is the base currency. Historic USD amounts convert at the Bangladesh Bank mid rate."""
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.db.models import Max

# Bangladesh Bank USD/BDT mid rate, 13 Aug 2026
USD_TO_BDT = Decimal('123.23')

SKIP_MODELS = {'Currency', 'CurrencyExchangeRate', 'TenantCurrency'}
SKIP_NAME_PARTS = (
    'percent',
    'pct',
    'quantity',
    'qty',
    'stock',
    'hours',
    'days',
    'minutes',
    'distance',
    'occupancy',
    'margin',
    'exchange',
)
SKIP_EXACT = {
    'tax_rate',
    'service_charge_rate',
    'commission_rate',
    'depreciation_rate',
    'sms_unit_cost',
    'decimal_places',
}


def usd_to_bdt(value, places=2):
    if value is None or value == '':
        return value
    quant = Decimal('1').scaleb(-places)
    return (Decimal(str(value)) * USD_TO_BDT).quantize(quant, rounding=ROUND_HALF_UP)


def _is_money_field(field):
    if not isinstance(field, models.DecimalField):
        return False
    name = field.name
    if name in SKIP_EXACT:
        return False
    if any(part in name for part in SKIP_NAME_PARTS):
        return False
    tokens = name.split('_')
    money_tokens = {
        'amount', 'price', 'cost', 'paid', 'due', 'balance', 'debit', 'credit',
        'salary', 'wage', 'fee', 'rent', 'pay', 'value', 'revenue', 'budget',
        'fine', 'sales', 'rate', 'allowance', 'allowances', 'bonus', 'discount',
        'subtotal', 'variance', 'limit',
    }
    return any(token in money_tokens for token in tokens)


def already_converted_to_bdt(apps=None):
    if apps is None:
        from django.apps import apps as django_apps
        apps = django_apps
    RoomType = apps.get_model('api', 'RoomType')
    MenuItem = apps.get_model('api', 'MenuItem')
    room_max = RoomType.objects.aggregate(m=Max('base_rate'))['m']
    if room_max is not None and room_max >= Decimal('500'):
        return True
    menu_max = MenuItem.objects.aggregate(m=Max('price'))['m']
    if menu_max is not None and menu_max >= Decimal('100'):
        return True
    return False


def convert_stored_usd_to_bdt(apps=None):
    """Multiply stored USD money fields by USD_TO_BDT. Idempotent for typical hotel data."""
    if apps is None:
        from django.apps import apps as django_apps
        apps = django_apps
    if already_converted_to_bdt(apps):
        return 0

    updated = 0
    models_iter = (
        apps.get_app_config('api').get_models()
        if hasattr(apps, 'get_app_config')
        else [m for m in apps.get_models() if m._meta.app_label == 'api']
    )
    for model in models_iter:
        if model.__name__ in SKIP_MODELS or not getattr(model._meta, 'managed', True):
            continue
        fields = [f for f in model._meta.local_fields if _is_money_field(f)]
        if not fields:
            continue
        for obj in model.objects.all().iterator():
            changed = []
            for field in fields:
                val = getattr(obj, field.name)
                if val is None:
                    continue
                setattr(obj, field.name, usd_to_bdt(val, field.decimal_places))
                changed.append(field.name)
            if changed:
                obj.save(update_fields=changed)
                updated += 1
    return updated
