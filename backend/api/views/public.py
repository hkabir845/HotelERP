"""Public (unauthenticated) APIs for tenant landing, booking, and ordering."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import Tenant
from api.models.tenant import ProductType
from api.services.catalog import (
    create_website_order,
    create_website_reservation,
    default_website_template,
    ensure_public_catalog,
    erp_catalog,
    lookup_stay,
    parse_datetime,
    pay_website_order,
    public_menu_items,
    public_room_types,
    public_rooms_list,
    public_tables,
)


def _platform_root_domain():
    import os
    return (os.environ.get('PLATFORM_ROOT_DOMAIN') or 'sascorporationbd.com').strip().lower().strip('.')


def _find_tenant(subdomain=None, domain=None, host=None):
    qs = Tenant.objects.filter(is_active=True)
    if subdomain:
        tenant = qs.filter(subdomain=str(subdomain).lower()).first()
        if tenant:
            return tenant
    if domain:
        d = str(domain).lower().split(':')[0]
        if d.startswith('www.'):
            d = d[4:]
        tenant = qs.filter(domain=d).first() or qs.filter(domain='www.' + d).first()
        if tenant:
            return tenant
    if host:
        host = str(host).split(':')[0].lower()
        if host.startswith('www.'):
            bare = host[4:]
        else:
            bare = host

        tenant = qs.filter(domain=host).first() or qs.filter(domain=bare).first()
        if tenant:
            return tenant

        root = _platform_root_domain()
        # turag.sascorporationbd.com → subdomain turag
        if root and (host == f'{host.split(".")[0]}.{root}' or host.endswith(f'.{root}')):
            if host not in (root, f'www.{root}'):
                sub = host[: -(len(root) + 1)]
                if sub and '.' not in sub:
                    tenant = qs.filter(subdomain=sub).first()
                    if tenant:
                        return tenant

        if '.' in host:
            sub = host.split('.')[0]
            if sub not in ('www', 'app', 'api', 'admin', 'saas'):
                tenant = qs.filter(subdomain=sub).first()
                if tenant:
                    return tenant
    return None


def _public_urls(tenant):
    """Equivalent public entry points for a tenant site."""
    root = _platform_root_domain()
    sub = (tenant.subdomain or '').lower()
    custom = (tenant.domain or '').strip().lower().lstrip('.')
    if custom.startswith('www.'):
        custom = custom[4:]
    urls = {
        'path': f'/site/{sub}',
        'saas': f'https://{sub}.{root}' if sub and root else None,
        'custom': f'https://{custom}' if custom else None,
    }
    return urls


def _tenant_ok(tenant):
    if not tenant:
        return Response({'detail': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
    if not tenant.is_active:
        return Response({'detail': 'Business is inactive'}, status=status.HTTP_403_FORBIDDEN)
    return None


def _subscription_blocked(tenant):
    from django.utils import timezone
    if tenant.subscription_expires_at and tenant.subscription_expires_at < timezone.now():
        return True
    return False


def _landing_payload(tenant):
    ensure_public_catalog(tenant)
    modules = tenant.get_enabled_modules()
    seo = tenant.get_seo()
    catalog = erp_catalog(tenant)
    template = tenant.landing_template or default_website_template(tenant.product_type, tenant.subdomain)
    return {
        'name': tenant.name,
        'subdomain': tenant.subdomain,
        'domain': tenant.domain,
        'public_urls': _public_urls(tenant),
        'product_type': tenant.product_type,
        'logo': tenant.logo,
        'landing_enabled': tenant.landing_enabled,
        'landing_title': tenant.landing_title or tenant.name,
        'landing_tagline': tenant.landing_tagline,
        'landing_template': template,
        'content': tenant.get_landing_content(),
        'seo': seo,
        'enabled_modules': modules,
        'city': tenant.city,
        'country': tenant.country,
        'address': tenant.address,
        'phone': tenant.phone,
        'email': tenant.email,
        'subscription_active': not _subscription_blocked(tenant),
        'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None,
        'ctas': {
            'book': tenant.product_type in (ProductType.HOTEL, ProductType.RESORT, ProductType.MIXED)
            and 'frontdesk' in modules,
            'order': 'fnb' in modules,
            'login': True,
        },
        'room_types': catalog['room_types'],
        'menu': catalog['menu'],
        'tables': catalog['tables'],
        'rooms': catalog['rooms'],
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def resolve_host(request):
    """Resolve tenant from Host / domain / subdomain query."""
    host = request.query_params.get('host') or request.META.get('HTTP_HOST', '')
    subdomain = request.query_params.get('subdomain')
    domain = request.query_params.get('domain')
    tenant = _find_tenant(subdomain=subdomain, domain=domain, host=host)
    if not tenant:
        return Response({'detail': 'No tenant for this host'}, status=status.HTTP_404_NOT_FOUND)
    if not tenant.landing_enabled or not tenant.has_module('landing'):
        return Response({'detail': 'Landing page disabled'}, status=status.HTTP_404_NOT_FOUND)
    return Response(_landing_payload(tenant))


@api_view(['GET'])
@permission_classes([AllowAny])
def public_landing(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.landing_enabled or not tenant.has_module('landing'):
        return Response({'detail': 'Landing page disabled'}, status=status.HTTP_404_NOT_FOUND)
    return Response(_landing_payload(tenant))


@api_view(['GET'])
@permission_classes([AllowAny])
def public_sites(request):
    """Public index of active landing pages for sitemap generation."""
    tenants = Tenant.objects.filter(is_active=True, landing_enabled=True)
    sites = []
    for tenant in tenants:
        if not tenant.has_module('landing'):
            continue
        sites.append({
            'subdomain': tenant.subdomain,
            'domain': tenant.domain,
            'name': tenant.name,
            'public_urls': _public_urls(tenant),
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None,
        })
    return Response({'sites': sites})


@api_view(['GET'])
@permission_classes([AllowAny])
def public_menu(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.has_module('fnb'):
        return Response({'detail': 'Restaurant module is not enabled'}, status=status.HTTP_403_FORBIDDEN)
    if _subscription_blocked(tenant):
        return Response({'detail': 'Subscription expired'}, status=status.HTTP_402_PAYMENT_REQUIRED)
    ensure_public_catalog(tenant)
    return Response({
        'tenant': tenant.subdomain,
        'items': public_menu_items(tenant),
        'tables': public_tables(tenant),
        'rooms': public_rooms_list(tenant),
        'fulfillment': ['restaurant', 'room'] if tenant.has_module('frontdesk') else ['restaurant'],
        'guest_kinds': (
            ['residential', 'booking', 'arrival', 'meal_only']
            if tenant.has_module('frontdesk')
            else ['meal_only']
        ),
        'payment': {
            'gateway': True,
            'methods': ['card', 'wallet'],
            'currency': tenant.currency or 'BDT',
        },
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def public_stays(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.has_module('frontdesk'):
        return Response({'detail': 'Booking is not available for this business'}, status=status.HTTP_403_FORBIDDEN)
    if _subscription_blocked(tenant):
        return Response({'detail': 'Subscription expired'}, status=status.HTTP_402_PAYMENT_REQUIRED)
    ensure_public_catalog(tenant)
    check_in = request.query_params.get('check_in')
    check_out = request.query_params.get('check_out')
    try:
        ci = parse_datetime(check_in, hotel_check_in=True) if check_in else None
        co = parse_datetime(check_out, hotel_check_out=True) if check_out else None
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'tenant': tenant.subdomain,
        'currency': tenant.currency or 'BDT',
        'room_types': public_room_types(tenant, ci, co),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def public_booking(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.has_module('frontdesk'):
        return Response({'detail': 'Booking is not available for this business'}, status=status.HTTP_403_FORBIDDEN)
    if _subscription_blocked(tenant):
        return Response(
            {'detail': 'Subscription expired. Please contact the business.'},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )
    ensure_public_catalog(tenant)
    try:
        booking = create_website_reservation(tenant, request.data or {})
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'message': 'Your stay is confirmed. Present this reference at check-in.',
        'reference': booking['reservation_number'],
        'booking': booking,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_stay_lookup(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.has_module('frontdesk'):
        return Response({'detail': 'Stay lookup is not available'}, status=status.HTTP_403_FORBIDDEN)
    try:
        stay = lookup_stay(tenant, request.query_params)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if not stay:
        return Response({'detail': 'Stay not required for meal-only orders'}, status=status.HTTP_200_OK)
    guest = stay.guest
    return Response({
        'ok': True,
        'reservation_number': stay.reservation_number,
        'status': stay.status,
        'guest_name': f'{guest.first_name} {guest.last_name}'.strip() if guest else '',
        'room_number': stay.room.room_number if stay.room_id else None,
        'check_in': stay.check_in_date.isoformat() if stay.check_in_date else None,
        'check_out': stay.check_out_date.isoformat() if stay.check_out_date else None,
        'charge_to_room': True,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def public_order(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.has_module('fnb'):
        return Response({'detail': 'Online ordering is not available'}, status=status.HTTP_403_FORBIDDEN)
    if _subscription_blocked(tenant):
        return Response({'detail': 'Subscription expired'}, status=status.HTTP_402_PAYMENT_REQUIRED)
    ensure_public_catalog(tenant)
    try:
        order = create_website_order(tenant, request.data or {})
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    where = 'your room' if order.get('serve_where') == 'room' else 'the restaurant'
    if order.get('checkout_required'):
        message = 'Order held for payment. Complete checkout to confirm and print.'
    elif order.get('payment_status') == 'room_charge':
        message = f'Order confirmed and charged to your room. We will serve it in {where}.'
    else:
        message = f'Order placed. We will serve it in {where} at the requested time.'
    return Response({
        'message': message,
        'order': order,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def public_order_pay(request, subdomain: str):
    tenant = _find_tenant(subdomain=subdomain)
    err = _tenant_ok(tenant)
    if err:
        return err
    if not tenant.has_module('fnb'):
        return Response({'detail': 'Online ordering is not available'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = pay_website_order(tenant, request.data or {})
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'message': order.get('message') or 'Payment successful',
        'order': order,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def public_leads_debug(request, subdomain: str):
    """Recent website reservations and orders for a tenant (ops helper)."""
    tenant = _find_tenant(subdomain=subdomain)
    if not tenant:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    from api.models import Order, Reservation
    bookings = list(
        Reservation.objects.filter(tenant=tenant, source='website')
        .order_by('-created_at')[:25]
        .values('reservation_number', 'status', 'check_in_date', 'total_amount', 'created_at')
    )
    orders = list(
        Order.objects.filter(tenant=tenant, order_number__startswith='WEB-')
        .order_by('-created_at')[:25]
        .values('order_number', 'status', 'order_type', 'total_amount', 'requested_at', 'created_at')
    )
    return Response({'bookings': bookings, 'orders': orders})
