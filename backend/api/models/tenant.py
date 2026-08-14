"""Tenant model for multi-tenant SaaS architecture."""
import json

from django.db import models


class ProductType(models.TextChoices):
    HOTEL = 'hotel', 'Hotel'
    RESORT = 'resort', 'Resort'
    RESTAURANT = 'restaurant', 'Restaurant'
    MIXED = 'mixed', 'Hotel + Restaurant'


# Canonical ERP modules that can be toggled per tenant
ALL_MODULES = [
    'frontdesk',
    'housekeeping',
    'fnb',
    'recipes',
    'laundry',
    'spa',
    'hall',
    'banquet',
    'pool',
    'crm',
    'accounts',
    'inventory',
    'assets',
    'broadcast',
    'hr',
    'channel',
    'reports',
    'utilities',
    'landing',
]

# Stay properties always include a restaurant. Restaurant-only subscriptions
# do not include hotel/resort operations.
HOTEL_ONLY_MODULES = ['frontdesk', 'housekeeping', 'assets']
RESTAURANT_MODULES = [
    'fnb', 'recipes', 'accounts', 'inventory', 'broadcast', 'reports', 'utilities', 'landing',
]
STAY_MODULES = [
    'frontdesk', 'housekeeping', 'fnb', 'recipes', 'laundry', 'spa', 'hall', 'banquet', 'pool', 'crm',
    'accounts', 'inventory', 'assets', 'broadcast', 'hr', 'channel', 'reports', 'utilities', 'landing',
]

MODULE_PRESETS = {
    ProductType.HOTEL: list(STAY_MODULES),
    ProductType.RESORT: list(STAY_MODULES),
    ProductType.RESTAURANT: list(RESTAURANT_MODULES),
    ProductType.MIXED: list(ALL_MODULES),
}


def modules_for_product(product_type):
    """Modules that may be selected for a subscription type."""
    if product_type == ProductType.RESTAURANT:
        return list(RESTAURANT_MODULES)
    return list(ALL_MODULES)

MODULE_LABELS = {
    'frontdesk': 'Frontdesk / Reservations',
    'housekeeping': 'Housekeeping',
    'fnb': 'Food & Beverage / Restaurant POS',
    'recipes': 'Recipe Management / Kitchen Stock',
    'laundry': 'Laundry POS',
    'spa': 'Spa & Beauty Salon',
    'hall': 'Hall Room',
    'banquet': 'Banquet / Events',
    'pool': 'Pool Booking',
    'crm': 'Sales & Marketing / CRM',
    'accounts': 'Accounts',
    'inventory': 'Inventory',
    'assets': 'Asset & Maintenance',
    'broadcast': 'Broadcast Messaging',
    'hr': 'HR / Employees',
    'channel': 'Channel Manager',
    'reports': 'Report Center',
    'utilities': 'Utilities / Settings',
    'landing': 'Public Landing Page',
}


class Tenant(models.Model):
    """Tenant model for multi-tenant SaaS."""

    name = models.CharField(max_length=255, unique=True, db_index=True)
    subdomain = models.CharField(max_length=100, unique=True, db_index=True)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    logo = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    subscription_plan = models.CharField(max_length=50, default='standard')
    subscription_expires_at = models.DateTimeField(null=True, blank=True)

    # SaaS product mode + module flags
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.HOTEL,
        db_index=True,
    )
    # Stored as JSON text for SQLite compatibility
    enabled_modules = models.TextField(default='[]', blank=True)

    # Public landing page basics
    landing_enabled = models.BooleanField(default=True)
    landing_title = models.CharField(max_length=255, null=True, blank=True)
    landing_tagline = models.CharField(max_length=500, null=True, blank=True)
    landing_template = models.CharField(max_length=50, default='default', blank=True)
    # Full website CMS blob (JSON text) — every public string/image is editable
    landing_content = models.TextField(default='{}', blank=True)

    # Per-tenant SEO
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.CharField(max_length=500, null=True, blank=True)
    og_image = models.CharField(max_length=500, null=True, blank=True)

    currency = models.CharField(max_length=8, default='BDT')
    timezone = models.CharField(max_length=64, default='Asia/Dhaka')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')
    time_format = models.CharField(max_length=8, default='12h')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'tenants'

    def __str__(self):
        return f"Tenant(id={self.id}, name='{self.name}', subdomain='{self.subdomain}')"

    def get_enabled_modules(self):
        """Return list of enabled module keys."""
        raw = (self.enabled_modules or '').strip()
        preset = list(MODULE_PRESETS.get(self.product_type, MODULE_PRESETS[ProductType.HOTEL]))
        if not raw:
            return preset
        try:
            data = json.loads(raw)
            if isinstance(data, list) and data:
                modules = [m for m in data if m in ALL_MODULES]
                # Stay properties inherit GYOROOM extras unless restaurant-only
                if 'frontdesk' in modules:
                    for extra in ('laundry', 'spa', 'hall', 'banquet', 'pool', 'crm', 'hr', 'channel'):
                        if extra not in modules:
                            modules.append(extra)
                return modules
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
        return preset

    def set_enabled_modules(self, modules):
        allowed = set(modules_for_product(self.product_type))
        cleaned = [m for m in (modules or []) if m in ALL_MODULES and m in allowed]
        if not cleaned:
            cleaned = list(MODULE_PRESETS.get(self.product_type, MODULE_PRESETS[ProductType.HOTEL]))
        # Recipe stock depends on the F&B kitchen
        if 'recipes' in cleaned and 'fnb' not in cleaned:
            cleaned.append('fnb')
        self.enabled_modules = json.dumps(cleaned)

    def apply_product_preset(self, product_type=None):
        """Set product_type and modules from preset."""
        if product_type:
            self.product_type = product_type
        self.set_enabled_modules(MODULE_PRESETS.get(self.product_type, MODULE_PRESETS[ProductType.HOTEL]))

    def has_module(self, module_key: str) -> bool:
        return module_key in self.get_enabled_modules()

    def get_landing_content(self):
        raw = (self.landing_content or '').strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}

    def set_landing_content(self, payload):
        if payload is None:
            self.landing_content = '{}'
            return
        if isinstance(payload, str):
            try:
                json.loads(payload)
                self.landing_content = payload
            except (TypeError, ValueError, json.JSONDecodeError):
                self.landing_content = '{}'
            return
        self.landing_content = json.dumps(payload)

    def get_seo(self):
        title = self.seo_title or self.landing_title or self.name
        description = self.seo_description or self.landing_tagline or ''
        return {
            'title': title,
            'description': description,
            'keywords': self.seo_keywords or '',
            'og_image': self.og_image or self.logo or '',
        }

    def to_saas_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'domain': self.domain,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'logo': self.logo,
            'is_active': self.is_active,
            'subscription_plan': self.subscription_plan,
            'subscription_expires_at': (
                self.subscription_expires_at.isoformat() if self.subscription_expires_at else None
            ),
            'product_type': self.product_type,
            'enabled_modules': self.get_enabled_modules(),
            'landing_enabled': self.landing_enabled,
            'landing_title': self.landing_title or self.name,
            'landing_tagline': self.landing_tagline,
            'landing_template': self.landing_template or 'default',
            'landing_content': self.get_landing_content(),
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'seo_keywords': self.seo_keywords,
            'og_image': self.og_image,
            'seo': self.get_seo(),
            'currency': self.currency or 'BDT',
            'timezone': self.timezone or 'Asia/Dhaka',
            'date_format': self.date_format or 'DD/MM/YYYY',
            'time_format': self.time_format or '12h',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
