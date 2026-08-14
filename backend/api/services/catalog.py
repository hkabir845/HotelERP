"""ERP catalog helpers shared by public websites and staff F&B."""
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from django.db.models import Q
from django.utils import timezone

from api.models import (
    Guest,
    Menu,
    MenuItem,
    Order,
    OrderItem,
    OrderStatus,
    OrderType,
    PosCustomer,
    Reservation,
    ReservationStatus,
    ReservationType,
    Room,
    RoomStatusEnum,
    RoomType,
    Table,
    TableStatus,
)
from api.models.tenant import ProductType

from api.money import usd_to_bdt

TAX_RATE = Decimal('0.10')

HOTEL_ROOM_TYPES = [
    ('Standard Twin', 'Two comfortable twin beds, city or garden outlook.', 2, usd_to_bdt(Decimal('89.00')), 'Wi-Fi, AC, TV, ensuite'),
    ('Deluxe King', 'King bed, work desk, and sitting area.', 2, usd_to_bdt(Decimal('129.00')), 'Wi-Fi, AC, minibar, ensuite'),
    ('Executive Suite', 'Separate living room, king bed, premium amenities.', 3, usd_to_bdt(Decimal('189.00')), 'Wi-Fi, lounge, bathtub'),
]

RESORT_ROOM_TYPES = [
    ('Deluxe Cottage', 'Riverside wooden cottage with a private deck.', 2, usd_to_bdt(Decimal('149.00')), 'Deck, river view, AC'),
    ('Family Suite', 'Two rooms for families, garden access.', 4, usd_to_bdt(Decimal('199.00')), 'Two bedrooms, sofa, kitchenette'),
    ('River Villa', 'Spacious villa over the water with lounge and dining.', 4, usd_to_bdt(Decimal('249.00')), 'Private deck, lounge, AC'),
]

DEFAULT_MENU = [
    ('Chicken Caesar Salad', 'Crisp romaine, grilled chicken, house dressing.', 'Salad', usd_to_bdt(Decimal('8.99'))),
    ('Seasonal Garden Salad', 'Local greens, citrus vinaigrette.', 'Salad', usd_to_bdt(Decimal('6.50'))),
    ('Grilled River Fish', 'Catch of the day with lemon butter and rice.', 'Mains', usd_to_bdt(Decimal('18.50'))),
    ('Beef Steak', 'Grilled steak, herb potatoes, garden vegetables.', 'Mains', usd_to_bdt(Decimal('22.00'))),
    ('Vegetable Pasta', 'Seasonal vegetables in a light tomato sauce.', 'Mains', usd_to_bdt(Decimal('12.50'))),
    ('Chicken Biryani', 'Aromatic rice, slow-cooked chicken, raita.', 'Mains', usd_to_bdt(Decimal('14.00'))),
    ('Chocolate Fondant', 'Warm chocolate cake with vanilla ice cream.', 'Desserts', usd_to_bdt(Decimal('7.50'))),
    ('Seasonal Fruit Platter', 'Fresh cut fruit from local farms.', 'Desserts', usd_to_bdt(Decimal('6.00'))),
    ('Fresh Lime Soda', 'House-pressed lime, soda, mint.', 'Beverages', usd_to_bdt(Decimal('2.50'))),
    ('Espresso', 'Double shot, freshly ground.', 'Beverages', usd_to_bdt(Decimal('3.00'))),
]

WEBSITE_TEMPLATES = {
    ProductType.HOTEL: 'hotel',
    ProductType.RESORT: 'resort',
    ProductType.RESTAURANT: 'restaurant',
    ProductType.MIXED: 'hotel',
}


def default_website_template(product_type, subdomain=''):
    if str(subdomain).lower() == 'turag':
        return 'turag'
    return WEBSITE_TEMPLATES.get(product_type, 'hotel')


def parse_datetime(value, *, end_of_day=False, hotel_check_in=False, hotel_check_out=False):
    if not value:
        raise ValueError('Date is required')
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace('Z', '+00:00')
        dt = None
        if len(text) >= 10 and text[4] == '-' and 'T' not in text[:11] and ' ' not in text[:11]:
            day = datetime.strptime(text[:10], '%Y-%m-%d')
            if hotel_check_in:
                dt = day.replace(hour=14, minute=0, second=0)
            elif hotel_check_out:
                dt = day.replace(hour=12, minute=0, second=0)
            elif end_of_day:
                dt = day.replace(hour=23, minute=59, second=0)
            else:
                dt = day
        else:
            try:
                dt = datetime.fromisoformat(text)
            except ValueError:
                for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S'):
                    try:
                        dt = datetime.strptime(text[:19], fmt)
                        break
                    except ValueError:
                        continue
        if dt is None:
            raise ValueError('Invalid date format')
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def conflicting_room_ids(tenant_id, check_in, check_out):
    return set(
        Reservation.objects.filter(
            tenant_id=tenant_id,
            status__in=[
                ReservationStatus.PENDING,
                ReservationStatus.CONFIRMED,
                ReservationStatus.CHECKED_IN,
            ],
            room_id__isnull=False,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
        ).values_list('room_id', flat=True)
    )


def available_rooms_qs(tenant, check_in, check_out, room_type_id=None):
    blocked = conflicting_room_ids(tenant.id, check_in, check_out)
    qs = Room.objects.select_related('room_type').filter(
        tenant_id=tenant.id,
        is_active=True,
    ).exclude(
        status__in=[
            RoomStatusEnum.OUT_OF_ORDER,
            RoomStatusEnum.MAINTENANCE,
        ]
    )
    if room_type_id:
        qs = qs.filter(room_type_id=room_type_id)
    if blocked:
        qs = qs.exclude(id__in=blocked)
    return qs


def serialize_room_type(rt, available_count=None):
    rooms = list(rt.rooms.filter(is_active=True))
    payload = {
        'id': rt.id,
        'name': rt.name,
        'description': rt.description or '',
        'max_occupancy': rt.max_occupancy,
        'base_rate': float(rt.base_rate) if rt.base_rate is not None else 0,
        'amenities': rt.amenities or '',
        'room_count': len(rooms),
    }
    if available_count is not None:
        payload['available_rooms'] = available_count
    return payload


def serialize_menu_item(item):
    return {
        'id': item.id,
        'name': item.name,
        'description': item.description or '',
        'price': float(item.price),
        'category': item.category or 'Mains',
        'image': item.image or None,
        'is_vegetarian': item.is_vegetarian,
        'is_available': item.is_available,
    }


def serialize_table(table):
    return {
        'id': table.id,
        'table_number': table.table_number,
        'capacity': table.capacity,
        'location': table.location or '',
        'status': table.status,
    }


def serialize_room_short(room):
    return {
        'id': room.id,
        'room_number': room.room_number,
        'room_type': room.room_type.name if room.room_type_id else '',
        'floor': room.floor,
        'status': room.status,
    }


def public_room_types(tenant, check_in=None, check_out=None):
    types = list(
        RoomType.objects.filter(tenant=tenant, is_active=True).prefetch_related('rooms')
    )
    blocked = set()
    if check_in and check_out:
        blocked = conflicting_room_ids(tenant.id, check_in, check_out)
    result = []
    for rt in types:
        rooms = [r for r in rt.rooms.all() if r.is_active]
        available = [
            r for r in rooms
            if r.id not in blocked and r.status not in (
                RoomStatusEnum.OUT_OF_ORDER,
                RoomStatusEnum.MAINTENANCE,
            )
        ]
        payload = serialize_room_type(rt, available_count=len(available) if check_in else len(rooms))
        result.append(payload)
    return result


def public_menu_items(tenant):
    return [
        serialize_menu_item(item)
        for item in MenuItem.objects.filter(
            tenant=tenant,
            is_available=True,
            menu__is_active=True,
        ).select_related('menu').order_by('category', 'name')
    ]


def public_tables(tenant):
    return [
        serialize_table(t)
        for t in Table.objects.filter(tenant=tenant, is_active=True).order_by('table_number')
    ]


def public_rooms_list(tenant):
    return [
        serialize_room_short(r)
        for r in Room.objects.filter(tenant=tenant, is_active=True)
        .select_related('room_type')
        .order_by('room_number')
    ]


def erp_catalog(tenant):
    """Live ERP data shown on public websites."""
    modules = tenant.get_enabled_modules()
    stays = public_room_types(tenant) if 'frontdesk' in modules else []
    menu = public_menu_items(tenant) if 'fnb' in modules else []
    tables = public_tables(tenant) if 'fnb' in modules else []
    rooms = public_rooms_list(tenant) if 'frontdesk' in modules or 'fnb' in modules else []
    return {
        'room_types': stays,
        'menu': menu,
        'tables': tables,
        'rooms': rooms,
    }


def seed_stay_catalog(tenant):
    if RoomType.objects.filter(tenant=tenant).exists():
        return
    if tenant.product_type == ProductType.RESTAURANT and 'frontdesk' not in tenant.get_enabled_modules():
        return
    specs = RESORT_ROOM_TYPES if tenant.product_type == ProductType.RESORT else HOTEL_ROOM_TYPES
    start_floor = 1
    for idx, (name, desc, occ, rate, amenities) in enumerate(specs, start=1):
        rt = RoomType.objects.create(
            tenant=tenant,
            name=name,
            description=desc,
            max_occupancy=occ,
            base_rate=rate,
            amenities=amenities,
            is_active=True,
        )
        floor = start_floor + idx - 1
        for n in range(1, 4):
            Room.objects.create(
                tenant=tenant,
                room_number=f'{floor}0{n}',
                room_type=rt,
                floor=floor,
                status=RoomStatusEnum.AVAILABLE,
                is_active=True,
                rack_rate=rate,
            )


def seed_fnb_catalog(tenant):
    if 'fnb' not in tenant.get_enabled_modules():
        return
    if not Menu.objects.filter(tenant=tenant).exists():
        menu = Menu.objects.create(
            tenant=tenant,
            name='All Day Dining',
            description='Website and restaurant menu',
            category='dining',
            is_active=True,
        )
        for name, desc, category, price in DEFAULT_MENU:
            MenuItem.objects.create(
                tenant=tenant,
                menu=menu,
                name=name,
                description=desc,
                category=category,
                price=price,
                is_available=True,
                is_vegetarian=name in (
                    'Seasonal Garden Salad',
                    'Vegetable Pasta',
                    'Seasonal Fruit Platter',
                    'Fresh Lime Soda',
                    'Espresso',
                ),
            )
    if not Table.objects.filter(tenant=tenant).exists():
        for i, cap in enumerate([2, 2, 4, 4, 4, 6, 6, 8], start=1):
            Table.objects.create(
                tenant=tenant,
                table_number=str(i),
                capacity=cap,
                status=TableStatus.AVAILABLE,
                location='Main dining',
                is_active=True,
            )


def ensure_public_catalog(tenant):
    """Fill empty ERP catalogs so a new website has rooms and a menu."""
    seed_stay_catalog(tenant)
    seed_fnb_catalog(tenant)


def split_guest_name(name):
    parts = [p for p in str(name or '').strip().split() if p]
    if not parts:
        return 'Guest', 'Guest'
    if len(parts) == 1:
        return parts[0], 'Guest'
    return parts[0], ' '.join(parts[1:])


def find_or_create_guest(tenant, name, email, phone):
    first, last = split_guest_name(name)
    guest = None
    if email:
        guest = Guest.objects.filter(tenant=tenant, email__iexact=email.strip()).first()
    if not guest and phone:
        guest = Guest.objects.filter(tenant=tenant, phone=phone.strip()).first()
    if guest:
        if email and not guest.email:
            guest.email = email.strip()
        if phone and not guest.phone:
            guest.phone = phone.strip()
        guest.save(update_fields=['email', 'phone', 'updated_at'])
        return guest
    return Guest.objects.create(
        tenant=tenant,
        first_name=first,
        last_name=last,
        email=(email or '').strip() or None,
        phone=(phone or '').strip() or None,
    )


def create_website_reservation(tenant, data):
    name = (data.get('name') or '').strip()
    check_in = parse_datetime(data.get('check_in') or data.get('check_in_date'), hotel_check_in=True)
    check_out = parse_datetime(data.get('check_out') or data.get('check_out_date'), hotel_check_out=True)
    if check_out <= check_in:
        raise ValueError('Check-out must be after check-in')
    guests = int(data.get('guests') or data.get('adults') or 1)
    room_type_id = data.get('room_type_id')
    if not name:
        raise ValueError('Guest name is required')
    if not room_type_id:
        raise ValueError('Please choose a room type')

    try:
        room_type = RoomType.objects.get(id=int(room_type_id), tenant=tenant, is_active=True)
    except (RoomType.DoesNotExist, TypeError, ValueError):
        raise ValueError('Room type was not found')

    if guests > (room_type.max_occupancy or 2) + 2:
        raise ValueError(f'This room type sleeps up to {room_type.max_occupancy} guests')

    room = available_rooms_qs(tenant, check_in, check_out, room_type.id).order_by('room_number').first()
    if not room:
        raise ValueError('No rooms of this type are available for those dates')

    nights = max((check_out.date() - check_in.date()).days, 1)
    rate = room.rack_rate or room_type.base_rate or Decimal('0')
    total = (rate * Decimal(nights)).quantize(Decimal('0.01'))
    guest = find_or_create_guest(
        tenant,
        name,
        data.get('email') or '',
        data.get('phone') or '',
    )
    reservation_number = f"WEB-{timezone.now().year}-{str(uuid.uuid4())[:8].upper()}"
    reservation = Reservation.objects.create(
        tenant=tenant,
        reservation_number=reservation_number,
        guest=guest,
        room=room,
        check_in_date=check_in,
        check_out_date=check_out,
        status=ReservationStatus.CONFIRMED,
        reservation_type=ReservationType.INDIVIDUAL,
        room_rate=rate,
        total_amount=total,
        paid_amount=Decimal('0'),
        balance=total,
        adults=guests,
        children=int(data.get('children') or 0),
        source='website',
        special_requests=data.get('notes') or data.get('special_requests') or '',
        notes='Self-booking from public website',
    )
    Room.objects.filter(id=room.id).update(status=RoomStatusEnum.RESERVED)
    return {
        'id': reservation.id,
        'reservation_number': reservation.reservation_number,
        'status': reservation.status,
        'guest_name': guest.full_name,
        'room_type': room_type.name,
        'room_number': room.room_number,
        'check_in': reservation.check_in_date.isoformat(),
        'check_out': reservation.check_out_date.isoformat(),
        'nights': nights,
        'room_rate': float(rate),
        'total_amount': float(total),
        'source': 'website',
    }


def _map_order_type(raw, serve_where):
    value = (raw or '').strip().lower()
    if serve_where == 'room' or value in ('room', 'room_service'):
        return OrderType.ROOM_SERVICE
    if value in ('takeaway', 'take_away'):
        return OrderType.TAKEAWAY
    if value in ('delivery',):
        return OrderType.DELIVERY
    return OrderType.DINE_IN


def _normalize_guest_kind(raw, created_by=None):
    value = (raw or '').strip().lower().replace('-', '_')
    aliases = {
        'in_house': 'residential',
        'resident': 'residential',
        'checked_in': 'residential',
        'confirmation': 'booking',
        'booking_confirmation': 'booking',
        'arriving': 'arrival',
        'on_arrival': 'arrival',
        'walk_in': 'meal_only' if not created_by else 'walk_in',
        'meal': 'meal_only',
        'website': 'meal_only',
    }
    value = aliases.get(value, value)
    allowed = {'walk_in', 'residential', 'booking', 'arrival', 'meal_only'}
    if value not in allowed:
        return 'walk_in' if created_by else 'meal_only'
    return value


def lookup_stay(tenant, data):
    """Match an in-house, confirmed-booking, or arriving guest."""
    kind = _normalize_guest_kind(data.get('guest_kind'), created_by=None)
    res_no = (data.get('reservation_number') or data.get('booking_ref') or '').strip()
    room_no = (data.get('room_number') or '').strip()
    phone = (data.get('customer_phone') or data.get('phone') or '').strip()
    qs = Reservation.objects.filter(tenant=tenant).select_related('guest', 'room')

    if kind == 'residential':
        qs = qs.filter(status=ReservationStatus.CHECKED_IN)
        if room_no:
            qs = qs.filter(room__room_number=room_no)
        if res_no:
            qs = qs.filter(reservation_number__iexact=res_no)
        if phone:
            qs = qs.filter(Q(guest__phone__icontains=phone) | Q(guest__mobile__icontains=phone))
        if not room_no and not res_no and not phone:
            raise ValueError('Enter your room number or booking reference to order as a residential guest')
        res = qs.order_by('-check_in_date').first()
        if not res:
            raise ValueError(
                'No in-house guest matched. Ask the front desk, or pay online for a meal-only order.'
            )
        return res

    if kind == 'booking':
        if not res_no:
            raise ValueError('Enter your booking confirmation number')
        res = qs.filter(
            reservation_number__iexact=res_no,
            status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN],
        ).first()
        if not res:
            raise ValueError('Booking confirmation not found')
        return res

    if kind == 'arrival':
        if not res_no:
            raise ValueError('Enter your booking confirmation for arrival')
        today = timezone.now().date()
        res = qs.filter(
            reservation_number__iexact=res_no,
            status__in=[ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN],
            check_out_date__date__gte=today,
        ).first()
        if not res:
            raise ValueError(
                'No arrival booking found. You can still order a meal and pay online.'
            )
        return res

    return None


def _serialize_order(order, serve_where=None, extra=None):
    if serve_where is None:
        serve_where = 'room' if order.order_type == OrderType.ROOM_SERVICE else 'restaurant'
    payload = {
        'id': order.id,
        'order_number': order.order_number,
        'status': order.status,
        'order_type': order.order_type,
        'source': order.source,
        'guest_kind': order.guest_kind,
        'payment_status': order.payment_status,
        'payment_method': order.payment_method,
        'checkout_ref': order.checkout_ref,
        'serve_where': serve_where,
        'room_number': order.room.room_number if order.room_id else None,
        'table_number': order.table.table_number if order.table_id else None,
        'reservation_number': order.reservation.reservation_number if order.reservation_id else None,
        'requested_at': order.requested_at.isoformat() if order.requested_at else None,
        'subtotal': float(order.subtotal or 0),
        'tax': float(order.tax_amount or 0),
        'total': float(order.total_amount or 0),
        'paid_amount': float(order.paid_amount or 0),
        'guest_name': order.guest_name,
        'checkout_required': order.payment_status in ('unpaid', 'pending'),
        'print_allowed': order.payment_status in ('paid', 'room_charge'),
    }
    if extra:
        payload.update(extra)
    return payload


def _deduct_if_needed(tenant, order, prepared_items, created_by=None):
    if not tenant.has_module('recipes'):
        return []
    from api.services.recipes import deduct_recipe_stock, ensure_recipe_catalog
    ensure_recipe_catalog(tenant)
    return deduct_recipe_stock(tenant, order, prepared_items, created_by=created_by)


def create_website_order(tenant, data, created_by=None):
    customer_name = (data.get('customer_name') or data.get('name') or '').strip()
    customer_phone = (data.get('customer_phone') or data.get('phone') or '').strip()
    items = data.get('items') or []
    serve_where = (data.get('serve_where') or data.get('fulfillment') or '').strip().lower()
    if serve_where in ('restaurant', 'dine_in', 'table'):
        serve_where = 'restaurant'
    elif serve_where in ('room', 'room_service'):
        serve_where = 'room'
    else:
        serve_where = 'restaurant' if not data.get('room_number') else 'room'

    guest_kind = _normalize_guest_kind(data.get('guest_kind'), created_by=created_by)
    if not created_by and guest_kind == 'walk_in':
        guest_kind = 'meal_only'

    pos_customer = None
    raw_cid = data.get('pos_customer_id')
    if raw_cid:
        try:
            pos_customer = PosCustomer.objects.get(tenant=tenant, id=int(raw_cid))
        except (PosCustomer.DoesNotExist, TypeError, ValueError):
            pos_customer = None
        if pos_customer:
            if not customer_name or customer_name.lower() == 'walk-in':
                customer_name = pos_customer.name
            if not customer_phone:
                customer_phone = pos_customer.phone or ''

    if not customer_name:
        raise ValueError('Guest name is required')
    if not items:
        raise ValueError('Add at least one menu item')

    stay = None
    if not created_by and guest_kind in ('residential', 'booking', 'arrival'):
        stay = lookup_stay(tenant, data)
        if stay and stay.guest_id and not customer_name:
            customer_name = f'{stay.guest.first_name} {stay.guest.last_name}'.strip()
        if stay and stay.room_id and not (data.get('room_number') or '').strip():
            data = dict(data)
            data['room_number'] = stay.room.room_number

    if serve_where == 'room' and not created_by and guest_kind == 'meal_only':
        raise ValueError(
            'Room delivery is for residential, booking-confirmation, or arriving guests. '
            'Meal-only guests pay online and are served at the restaurant.'
        )

    requested_raw = data.get('requested_at') or data.get('serve_at') or data.get('delivery_time')
    if requested_raw:
        requested_at = parse_datetime(requested_raw)
        if requested_at < timezone.now() - timedelta(minutes=5):
            raise ValueError('Please choose a serve time from now onward')
    else:
        requested_at = timezone.now()

    room = None
    table = None
    room_number = (data.get('room_number') or '').strip()
    if stay and stay.room_id and not room_number:
        room_number = stay.room.room_number
    table_number = str(data.get('table_number') or '').strip()
    table_id = data.get('table_id')

    if serve_where == 'room':
        if not room_number:
            raise ValueError('Room number is required for in-room service')
        room = Room.objects.filter(tenant=tenant, room_number=room_number, is_active=True).first()
        if not room:
            raise ValueError(f'Room {room_number} was not found')
    else:
        if table_id:
            table = Table.objects.filter(tenant=tenant, id=table_id, is_active=True).first()
        elif table_number:
            table = Table.objects.filter(tenant=tenant, table_number=table_number, is_active=True).first()

    pay_method = (data.get('payment_method') or '').strip().lower()
    if created_by:
        source = 'pos'
        if pay_method in ('room_charge', 'room'):
            payment_status = 'room_charge'
            pay_method = 'room_charge'
        elif pay_method in ('later', 'unpaid', ''):
            payment_status = 'unpaid'
            pay_method = pay_method or 'later'
        else:
            payment_status = 'paid'
            pay_method = pay_method or 'cash'
        finalize = True
    elif guest_kind in ('residential', 'booking', 'arrival') and pay_method in ('room_charge', 'room', ''):
        source = 'website'
        payment_status = 'room_charge'
        pay_method = 'room_charge'
        finalize = True
    else:
        source = 'website'
        payment_status = 'pending'
        pay_method = 'gateway'
        finalize = False

    order_type = _map_order_type(data.get('order_type'), serve_where)
    subtotal = Decimal('0')
    prepared_items = []
    for row in items:
        item_id = row.get('menu_item_id') or row.get('id')
        qty = int(row.get('quantity') or 0)
        if not item_id or qty < 1:
            continue
        menu_item = MenuItem.objects.filter(
            tenant=tenant,
            id=int(item_id),
            is_available=True,
        ).first()
        if not menu_item:
            raise ValueError('A menu item is no longer available')
        line = (menu_item.price * Decimal(qty)).quantize(Decimal('0.01'))
        subtotal += line
        prepared_items.append((menu_item, qty, menu_item.price, line, row.get('special_instructions') or ''))

    if not prepared_items:
        raise ValueError('Add at least one valid menu item')

    tax = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
    total = subtotal + tax
    prefix = 'POS' if created_by else 'WEB'
    order_number = f"{prefix}-{timezone.now().year}-{str(uuid.uuid4())[:8].upper()}"
    checkout_ref = None if finalize else f"PAY-{str(uuid.uuid4())[:12].upper()}"
    notes_bits = [data.get('notes') or '']
    notes_bits.append(
        f'Serve: {"in room" if serve_where == "room" else "at restaurant"} '
        f'at {requested_at.strftime("%Y-%m-%d %H:%M")}'
    )
    notes_bits.append(f'Guest: {guest_kind}')
    if data.get('customer_email'):
        notes_bits.append(f'Email: {data.get("customer_email")}')
    order = Order.objects.create(
        tenant=tenant,
        order_number=order_number,
        order_type=order_type,
        status=OrderStatus.CONFIRMED if finalize else OrderStatus.PENDING,
        table=table,
        room=room,
        reservation=stay,
        guest_name=customer_name,
        guest_phone=customer_phone or None,
        revenue_center=(data.get('revenue_center') or '').strip() or (
            'Room Service' if order_type == OrderType.ROOM_SERVICE else 'Restaurant'
        ),
        pos_customer=pos_customer,
        subtotal=subtotal,
        tax_amount=tax,
        total_amount=total,
        paid_amount=total if payment_status == 'paid' else Decimal('0'),
        requested_at=requested_at,
        special_instructions=data.get('special_instructions') or '',
        notes=' | '.join([b for b in notes_bits if b]),
        created_by=created_by,
        source=source,
        guest_kind=guest_kind,
        payment_status=payment_status,
        payment_method=pay_method or None,
        checkout_ref=checkout_ref,
    )
    for menu_item, qty, unit, line, instr in prepared_items:
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=qty,
            unit_price=unit,
            total_price=line,
            special_instructions=instr or None,
            status='pending',
        )
    stock_moves = _deduct_if_needed(tenant, order, prepared_items, created_by=created_by) if finalize else []
    extra = {
        'stock_deductions': stock_moves,
        'low_stock_after_order': [m for m in stock_moves if m.get('is_low_stock') or m.get('shortfall')],
        'message': (
            'Order sent to the kitchen.'
            if finalize
            else 'Checkout started. Pay to confirm the order, then you can print.'
        ),
    }
    return _serialize_order(order, serve_where, extra)


def pay_website_order(tenant, data):
    checkout_ref = (data.get('checkout_ref') or '').strip()
    order_number = (data.get('order_number') or '').strip()
    if not checkout_ref and not order_number:
        raise ValueError('Checkout reference is required')

    qs = Order.objects.filter(tenant=tenant)
    order = qs.filter(checkout_ref=checkout_ref).first() if checkout_ref else None
    if not order and order_number:
        order = qs.filter(order_number=order_number).first()
    if not order:
        raise ValueError('Checkout session not found')
    if order.payment_status in ('paid', 'room_charge'):
        return _serialize_order(order, extra={'message': 'Already paid'})

    method = (data.get('payment_method') or data.get('method') or 'card').strip().lower()
    if method in ('bkash', 'nagad', 'wallet', 'mobile'):
        method = 'wallet'
    elif method in ('card', 'visa', 'mastercard', 'gateway'):
        method = 'card'
    else:
        method = 'card'

    card_number = ''.join(ch for ch in str(data.get('card_number') or '') if ch.isdigit())
    if method == 'card':
        if card_number == '4000000000000002':
            raise ValueError('Card declined. Try another card or mobile wallet.')
        if len(card_number) < 13:
            raise ValueError('Enter a valid card number')
    wallet_ref = (data.get('wallet_number') or data.get('mobile_number') or '').strip()
    if method == 'wallet' and len(wallet_ref) < 8:
        raise ValueError('Enter your mobile wallet number')

    prepared_items = [
        (item.menu_item, item.quantity, item.unit_price, item.total_price, item.special_instructions or '')
        for item in order.items.select_related('menu_item').all()
    ]
    order.payment_status = 'paid'
    order.payment_method = method
    order.paid_amount = order.total_amount
    order.status = OrderStatus.CONFIRMED
    last4 = card_number[-4:] if card_number else ''
    stamp = f'Paid via {method}' + (f' ····{last4}' if last4 else '')
    order.notes = (order.notes or '') + f' | {stamp}'
    order.save(update_fields=[
        'payment_status', 'payment_method', 'paid_amount', 'status', 'notes', 'updated_at',
    ])
    stock_moves = _deduct_if_needed(tenant, order, prepared_items)
    return _serialize_order(order, extra={
        'message': 'Payment successful. Your order is confirmed.',
        'stock_deductions': stock_moves,
        'low_stock_after_order': [m for m in stock_moves if m.get('is_low_stock') or m.get('shortfall')],
        'paid': True,
        'print_allowed': True,
        'checkout_required': False,
    })


def serialize_staff_order(order):
    return {
        'id': order.id,
        'order_number': order.order_number,
        'order_type': order.order_type,
        'customer_name': order.guest_name,
        'customer_phone': order.guest_phone,
        'room_number': order.room.room_number if order.room_id else None,
        'table_number': order.table.table_number if order.table_id else None,
        'status': order.status,
        'total': float(order.total_amount or 0),
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'requested_at': order.requested_at.isoformat() if order.requested_at else None,
        'items_count': order.items.count() if hasattr(order, 'items') else 0,
        'notes': order.notes or '',
        'source': getattr(order, 'source', None) or (
            'website' if (order.order_number or '').startswith('WEB-') else 'pos'
        ),
        'guest_kind': getattr(order, 'guest_kind', None),
        'payment_status': getattr(order, 'payment_status', None),
        'payment_method': getattr(order, 'payment_method', None),
    }
