"""Superadmin SaaS control panel endpoints."""
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    Bill,
    BillStatus,
    Employee,
    Guest,
    Reservation,
    ReservationStatus,
    Room,
    Tenant,
    User,
    UserRole,
    WorkOrder,
)
from api.models.tenant import (
    ALL_MODULES,
    MODULE_LABELS,
    MODULE_PRESETS,
    ProductType,
    modules_for_product,
)
from api.services.catalog import default_website_template, ensure_public_catalog


ALLOWED_CURRENCIES = ('BDT', 'USD', 'EUR', 'GBP', 'INR', 'AED', 'SAR')
ALLOWED_DATE_FORMATS = ('DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD', 'DD-MM-YYYY')
ALLOWED_TIME_FORMATS = ('12h', '24h')
ALLOWED_TIMEZONES = (
    'Asia/Dhaka',
    'UTC',
    'Asia/Kolkata',
    'Asia/Dubai',
    'Europe/London',
    'America/New_York',
)


def _tenant_admin(tenant):
    return (
        User.objects.filter(tenant_id=tenant.id, role=UserRole.ADMIN).order_by('id').first()
        or User.objects.filter(tenant_id=tenant.id, is_staff=True, is_superuser=False)
        .order_by('id')
        .first()
    )


def _admin_payload(tenant):
    admin = _tenant_admin(tenant)
    if not admin:
        return None
    return {
        'id': admin.id,
        'username': admin.username,
        'email': admin.email,
    }


def _upsert_tenant_admin(tenant, data):
    username = (data.get('admin_username') or '').strip()
    email = (data.get('admin_email') or '').strip()
    password = data.get('admin_password')
    if password is not None:
        password = str(password)
    if not username and not email and not password:
        return None

    admin = _tenant_admin(tenant)
    if username and User.objects.filter(username=username).exclude(id=getattr(admin, 'id', 0)).exists():
        return 'Username already exists'
    if email and User.objects.filter(email=email).exclude(id=getattr(admin, 'id', 0)).exists():
        return 'Email already exists'

    if not admin:
        if not username or not password:
            return 'Admin username and password are required to create a login'
        admin = User(
            username=username,
            email=email or f'{username}@{tenant.subdomain}.local',
            first_name='Admin',
            last_name=tenant.name[:40],
            role=UserRole.ADMIN,
            tenant=tenant,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        admin.set_password(password)
        admin.save()
        return None

    if username:
        admin.username = username
    if email:
        admin.email = email
    if password:
        admin.set_password(password)
    admin.is_active = True
    admin.is_staff = True
    admin.save()
    return None


def _require_superuser(user):
    if not user or not getattr(user, 'is_superuser', False):
        return Response(
            {'detail': 'Only superusers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


def _parse_expiry(value):
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        dt = None
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(text[:19] if 'T' in text else text[:10], fmt)
                break
            except ValueError:
                continue
        if dt is None:
            return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    # Date-only expiry means end of that calendar day
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and len(str(value).strip()) <= 10:
        dt = dt + timedelta(hours=23, minutes=59, seconds=59)
    return dt


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def catalog(request):
    """Return product types, plans, and module catalog."""
    denied = _require_superuser(request.user)
    if denied:
        return denied

    return Response({
        'product_types': [
            {
                'key': key,
                'label': label,
                'modules': MODULE_PRESETS.get(key, []),
                'available_modules': modules_for_product(key),
            }
            for key, label in ProductType.choices
        ],
        'modules': [
            {'key': key, 'label': MODULE_LABELS.get(key, key)}
            for key in ALL_MODULES
        ],
        'plans': [
            {'key': 'starter', 'label': 'Starter'},
            {'key': 'standard', 'label': 'Standard'},
            {'key': 'premium', 'label': 'Premium'},
            {'key': 'enterprise', 'label': 'Enterprise'},
        ],
        'website_templates': [
            {'key': 'hotel', 'label': 'Professional hotel', 'product_types': ['hotel', 'mixed']},
            {'key': 'resort', 'label': 'Professional resort', 'product_types': ['resort', 'mixed']},
            {'key': 'restaurant', 'label': 'Professional restaurant', 'product_types': ['restaurant', 'hotel', 'resort', 'mixed']},
            {'key': 'turag', 'label': 'Turag Waterfront (signature resort)', 'product_types': ['resort', 'mixed']},
        ],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """Get superadmin SaaS dashboard statistics."""
    denied = _require_superuser(request.user)
    if denied:
        return denied

    total_tenants = Tenant.objects.count()
    active_tenants = Tenant.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    by_product = {}
    for key, _label in ProductType.choices:
        by_product[key] = Tenant.objects.filter(product_type=key).count()

    tenant_stats = []
    for tenant in Tenant.objects.all().order_by('-created_at'):
        total_rooms = Room.objects.filter(tenant_id=tenant.id).count()
        occupied_rooms = Room.objects.filter(tenant_id=tenant.id, status='occupied').count()
        revenue = Bill.objects.filter(
            tenant_id=tenant.id,
            status=BillStatus.PAID,
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal(0)

        tenant_stats.append({
            'tenant_id': tenant.id,
            'tenant_name': tenant.name,
            'subdomain': tenant.subdomain,
            'is_active': tenant.is_active,
            'subscription_plan': tenant.subscription_plan,
            'product_type': tenant.product_type,
            'enabled_modules': tenant.get_enabled_modules(),
            'statistics': {
                'reservations': {
                    'total': Reservation.objects.filter(tenant_id=tenant.id).count(),
                    'active': Reservation.objects.filter(
                        tenant_id=tenant.id,
                        status__in=[ReservationStatus.CHECKED_IN, ReservationStatus.CONFIRMED],
                    ).count(),
                },
                'rooms': {
                    'total': total_rooms,
                    'occupied': occupied_rooms,
                    'occupancy_rate': round(
                        (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2
                    ),
                },
                'guests': {'total': Guest.objects.filter(tenant_id=tenant.id).count()},
                'revenue': {'total': float(revenue)},
                'employees': {'total': Employee.objects.filter(tenant_id=tenant.id).count()},
                'work_orders': {
                    'pending': WorkOrder.objects.filter(
                        tenant_id=tenant.id,
                        status__in=['pending', 'in_progress'],
                    ).count()
                },
            },
        })

    total_revenue = Bill.objects.filter(status=BillStatus.PAID).aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal(0)

    return Response({
        'overview': {
            'tenants': {'total': total_tenants, 'active': active_tenants},
            'users': {'total': total_users, 'active': active_users},
            'reservations': {'total': Reservation.objects.count()},
            'rooms': {'total': Room.objects.count()},
            'guests': {'total': Guest.objects.count()},
            'revenue': {'total': float(total_revenue)},
            'by_product_type': by_product,
        },
        'tenants': tenant_stats,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tenants(request):
    """List or create tenants (superadmin only)."""
    denied = _require_superuser(request.user)
    if denied:
        return denied

    if request.method == 'GET':
        try:
            skip = max(0, int(request.query_params.get('skip', 0) or 0))
            limit = min(max(1, int(request.query_params.get('limit', 100) or 100)), 500)
        except (TypeError, ValueError):
            skip, limit = 0, 100
        product_type = request.query_params.get('product_type')
        qs = Tenant.objects.all().order_by('-created_at')
        if product_type:
            qs = qs.filter(product_type=product_type)
        total = qs.count()
        tenants_list = qs[skip:skip + limit]
        return Response({
            'total': total,
            'tenants': [t.to_saas_dict() for t in tenants_list],
        })

    data = request.data
    name = (data.get('name') or '').strip()
    subdomain = (data.get('subdomain') or '').strip().lower()
    email = (data.get('email') or '').strip()
    if not name or not subdomain or not email:
        return Response(
            {'detail': 'name, subdomain, and email are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if Tenant.objects.filter(subdomain=subdomain).exists():
        return Response({'detail': 'Subdomain already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if Tenant.objects.filter(name=name).exists():
        return Response({'detail': 'Tenant name already exists'}, status=status.HTTP_400_BAD_REQUEST)

    product_type = data.get('product_type') or ProductType.HOTEL
    if product_type not in dict(ProductType.choices):
        product_type = ProductType.HOTEL

    tenant = Tenant(
        name=name,
        subdomain=subdomain,
        domain=data.get('domain') or None,
        email=email,
        phone=data.get('phone') or None,
        address=data.get('address') or None,
        city=data.get('city') or None,
        country=data.get('country') or None,
        is_active=bool(data.get('is_active', True)),
        subscription_plan=data.get('subscription_plan') or 'standard',
        subscription_expires_at=_parse_expiry(data.get('subscription_expires_at')),
        product_type=product_type,
        landing_enabled=bool(data.get('landing_enabled', True)),
        landing_title=data.get('landing_title') or name,
        landing_tagline=data.get('landing_tagline') or '',
        landing_template=data.get('landing_template') or default_website_template(
            product_type, subdomain
        ),
        seo_title=data.get('seo_title') or None,
        seo_description=data.get('seo_description') or None,
        seo_keywords=data.get('seo_keywords') or None,
        og_image=data.get('og_image') or None,
        currency=data.get('currency') if data.get('currency') in ALLOWED_CURRENCIES else 'BDT',
        timezone=data.get('timezone') if data.get('timezone') in ALLOWED_TIMEZONES else 'Asia/Dhaka',
        date_format=data.get('date_format') if data.get('date_format') in ALLOWED_DATE_FORMATS else 'DD/MM/YYYY',
        time_format=data.get('time_format') if data.get('time_format') in ALLOWED_TIME_FORMATS else '12h',
    )
    if data.get('enabled_modules'):
        tenant.set_enabled_modules(data.get('enabled_modules'))
    else:
        tenant.apply_product_preset(product_type)
    if data.get('landing_content') is not None:
        tenant.set_landing_content(data.get('landing_content'))
    tenant.save()

    # Optional bootstrap admin for the tenant
    admin_email = (data.get('admin_email') or '').strip()
    admin_password = data.get('admin_password') or 'Admin@123'
    admin_username = (data.get('admin_username') or subdomain + '_admin').strip()
    if admin_email and not User.objects.filter(email=admin_email).exists():
        admin = User(
            username=admin_username,
            email=admin_email,
            first_name=data.get('admin_first_name') or 'Admin',
            last_name=data.get('admin_last_name') or 'User',
            role=UserRole.ADMIN,
            tenant=tenant,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        admin.set_password(admin_password)
        admin.save()

    ensure_public_catalog(tenant)

    return Response(tenant.to_saas_dict(), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def tenant_detail(request, tenant_id: int):
    """Retrieve, update, or delete a tenant."""
    denied = _require_superuser(request.user)
    if denied:
        return denied

    tenant = Tenant.objects.filter(id=tenant_id).first()
    if not tenant:
        return Response({'detail': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        User.objects.filter(tenant_id=tenant.id).update(is_active=False, tenant=None)
        tenant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'GET':
        payload = tenant.to_saas_dict()
        payload['user_count'] = User.objects.filter(tenant_id=tenant.id).count()
        payload['admin'] = _admin_payload(tenant)
        return Response(payload)

    data = request.data
    for field in (
        'name', 'domain', 'email', 'phone', 'address', 'city', 'state',
        'country', 'postal_code', 'logo', 'subscription_plan',
        'landing_title', 'landing_tagline', 'landing_template',
        'seo_title', 'seo_description', 'seo_keywords', 'og_image',
    ):
        if field in data:
            setattr(tenant, field, data.get(field) or None if field != 'name' else data.get(field))

    if 'currency' in data and data.get('currency') in ALLOWED_CURRENCIES:
        tenant.currency = data['currency']
    if 'timezone' in data and data.get('timezone') in ALLOWED_TIMEZONES:
        tenant.timezone = data['timezone']
    if 'date_format' in data and data.get('date_format') in ALLOWED_DATE_FORMATS:
        tenant.date_format = data['date_format']
    if 'time_format' in data and data.get('time_format') in ALLOWED_TIME_FORMATS:
        tenant.time_format = data['time_format']

    if 'subdomain' in data and data.get('subdomain'):
        new_sub = str(data['subdomain']).strip().lower()
        if new_sub != tenant.subdomain and Tenant.objects.filter(subdomain=new_sub).exists():
            return Response({'detail': 'Subdomain already exists'}, status=status.HTTP_400_BAD_REQUEST)
        tenant.subdomain = new_sub

    if 'is_active' in data:
        tenant.is_active = bool(data.get('is_active'))
    if 'landing_enabled' in data:
        tenant.landing_enabled = bool(data.get('landing_enabled'))
    if 'subscription_expires_at' in data:
        tenant.subscription_expires_at = _parse_expiry(data.get('subscription_expires_at'))

    if 'product_type' in data and data.get('product_type') in dict(ProductType.choices):
        tenant.product_type = data['product_type']
        # If modules not explicitly sent, apply preset for new product type
        if 'enabled_modules' not in data:
            tenant.apply_product_preset()

    if 'enabled_modules' in data:
        tenant.set_enabled_modules(data.get('enabled_modules'))

    if 'landing_content' in data:
        tenant.set_landing_content(data.get('landing_content'))

    if data.get('apply_preset'):
        tenant.apply_product_preset()

    admin_error = _upsert_tenant_admin(tenant, data)
    if admin_error:
        return Response({'detail': admin_error}, status=status.HTTP_400_BAD_REQUEST)

    tenant.save()
    payload = tenant.to_saas_dict()
    payload['admin'] = _admin_payload(tenant)
    return Response(payload)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue(request):
    """Get revenue statistics (superadmin only)."""
    denied = _require_superuser(request.user)
    if denied:
        return denied

    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)

    revenue_by_tenant = (
        Bill.objects.filter(
            status=BillStatus.PAID,
            bill_date__gte=start_date.date(),
        )
        .values('tenant__name', 'tenant__subdomain', 'tenant__product_type')
        .annotate(revenue=Sum('total_amount'))
    )

    total_revenue = Bill.objects.filter(
        status=BillStatus.PAID,
        bill_date__gte=start_date.date(),
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal(0)

    return Response({
        'period_days': days,
        'total_revenue': float(total_revenue),
        'revenue_by_tenant': [
            {
                'tenant_name': r['tenant__name'],
                'subdomain': r['tenant__subdomain'],
                'product_type': r['tenant__product_type'],
                'revenue': float(r['revenue'] or 0),
            }
            for r in revenue_by_tenant
        ],
    })
