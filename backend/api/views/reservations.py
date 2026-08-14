"""Reservations endpoints."""
import uuid
from datetime import datetime
from decimal import Decimal

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import Guest, Reservation, ReservationStatus, ReservationType, Room, RoomStatusEnum
from api.services.catalog import available_rooms_qs, parse_datetime
from api.views import deny_if_no_tenant


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reservations(request):
    """Get list of reservations with pagination."""
    current_user = request.user
    denied = deny_if_no_tenant(current_user)
    if denied:
        return denied

    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 200))
    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')
    reservation_type = request.query_params.get('reservation_type')
    check_in_date = request.query_params.get('check_in_date')
    check_out_date = request.query_params.get('check_out_date')
    check_in_from = request.query_params.get('check_in_date_from') or request.query_params.get('check_in_from')
    check_in_to = request.query_params.get('check_in_date_to') or request.query_params.get('check_in_to')
    tenant_id = current_user.tenant_id

    qs = Reservation.objects.select_related('guest', 'room', 'room__room_type')
    if tenant_id:
        qs = qs.filter(tenant_id=tenant_id)

    if status_filter:
        statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
        valid = [s for s in statuses if s in ReservationStatus.values]
        if len(valid) == 1:
            qs = qs.filter(status=valid[0])
        elif valid:
            qs = qs.filter(status__in=valid)

    if reservation_type and reservation_type in ReservationType.values:
        qs = qs.filter(reservation_type=reservation_type)

    if check_in_date:
        qs = qs.filter(check_in_date__date=check_in_date)
    if check_out_date:
        qs = qs.filter(check_out_date__date=check_out_date)
    if check_in_from:
        qs = qs.filter(check_in_date__date__gte=check_in_from)
    if check_in_to:
        qs = qs.filter(check_in_date__date__lte=check_in_to)

    if search:
        qs = qs.filter(
            Q(reservation_number__icontains=search)
            | Q(guest__first_name__icontains=search)
            | Q(guest__last_name__icontains=search)
            | Q(guest__email__icontains=search)
            | Q(guest__phone__icontains=search)
        )

    total = qs.count()
    total_pages = (total + limit - 1) // limit
    reservations = qs.order_by('-check_in_date')[(page - 1) * limit:page * limit]

    result = []
    for res in reservations:
        nights = 0
        if res.check_in_date and res.check_out_date:
            nights = (res.check_out_date - res.check_in_date).days
        result.append({
            'id': res.id,
            'reservation_number': res.reservation_number,
            'registration_number': res.reservation_number,
            'guest': {
                'id': res.guest.id,
                'name': f'{res.guest.first_name} {res.guest.last_name}',
                'email': res.guest.email,
                'phone': res.guest.phone,
                'is_vip': res.guest.is_vip,
            },
            'room': {
                'id': res.room.id,
                'room_number': res.room.room_number,
                'room_type': res.room.room_type.name,
            } if res.room else None,
            'check_in_date': res.check_in_date.isoformat() if res.check_in_date else None,
            'check_out_date': res.check_out_date.isoformat() if res.check_out_date else None,
            'actual_check_in': res.actual_check_in.isoformat() if res.actual_check_in else None,
            'actual_check_out': res.actual_check_out.isoformat() if res.actual_check_out else None,
            'status': res.status,
            'reservation_type': res.reservation_type,
            'adults': res.adults,
            'children': res.children,
            'room_rate': float(res.room_rate) if res.room_rate else None,
            'total_amount': float(res.total_amount) if res.total_amount else None,
            'paid_amount': float(res.paid_amount) if res.paid_amount else None,
            'balance': float(res.balance) if res.balance else None,
            'source': res.source,
            'nights': nights,
        })

    return Response({
        'reservations': result,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reservation(request):
    """Create a new reservation."""
    current_user = request.user
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        return Response(
            {'detail': 'Tenant access required'},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data
    guest_id = data.get('guest_id')
    guest_data = data.get('guest')

    if not guest_id:
        if not guest_data:
            return Response(
                {'detail': 'Either guest_id or guest information is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_guest = None
        if guest_data.get('email'):
            existing_guest = Guest.objects.filter(
                email=guest_data['email'],
                tenant_id=tenant_id,
            ).first()
        elif guest_data.get('phone'):
            existing_guest = Guest.objects.filter(
                phone=guest_data['phone'],
                tenant_id=tenant_id,
            ).first()

        if existing_guest:
            guest_id = existing_guest.id
        else:
            dob = None
            if guest_data.get('date_of_birth'):
                try:
                    dob = datetime.strptime(guest_data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    pass

            new_guest = Guest.objects.create(
                tenant_id=tenant_id,
                first_name=guest_data['first_name'],
                last_name=guest_data['last_name'],
                email=guest_data.get('email'),
                phone=guest_data.get('phone'),
                mobile=guest_data.get('mobile'),
                address_line1=guest_data.get('address_line1'),
                city=guest_data.get('city'),
                state=guest_data.get('state'),
                country=guest_data.get('country'),
                postal_code=guest_data.get('postal_code'),
                id_type=guest_data.get('id_type'),
                id_number=guest_data.get('id_number'),
                date_of_birth=dob,
                nationality=guest_data.get('nationality'),
                gender=guest_data.get('gender'),
                is_vip=guest_data.get('is_vip', False),
            )
            guest_id = new_guest.id

    try:
        guest = Guest.objects.get(id=guest_id)
    except Guest.DoesNotExist:
        return Response({'detail': 'Guest not found'}, status=status.HTTP_404_NOT_FOUND)

    room_id = data.get('room_id')
    room_type_id = data.get('room_type_id')
    if not room_id and room_type_id:
        available_room = Room.objects.filter(
            room_type_id=room_type_id,
            tenant_id=tenant_id,
            status=RoomStatusEnum.AVAILABLE,
            is_active=True,
        ).first()
        if available_room:
            room_id = available_room.id

    try:
        check_in = datetime.fromisoformat(data['check_in_date'].replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(data['check_out_date'].replace('Z', '+00:00'))
    except (ValueError, KeyError, AttributeError):
        return Response(
            {'detail': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if check_out <= check_in:
        return Response(
            {'detail': 'Check-out date must be after check-in date'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    nights = (check_out - check_in).days
    room_rate = Decimal(str(data['room_rate']))
    total_amount = data.get('total_amount')
    if total_amount is not None:
        total_amount = Decimal(str(total_amount))
    else:
        total_amount = room_rate * Decimal(nights)

    paid_amount = Decimal(str(data.get('paid_amount', 0)))
    balance = total_amount - paid_amount
    reservation_number = f"RES-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"

    reservation = Reservation.objects.create(
        tenant_id=tenant_id,
        reservation_number=reservation_number,
        guest_id=guest_id,
        room_id=room_id,
        check_in_date=check_in,
        check_out_date=check_out,
        status=data.get('status', ReservationStatus.PENDING),
        reservation_type=data.get('reservation_type', ReservationType.INDIVIDUAL),
        room_rate=room_rate,
        total_amount=total_amount,
        paid_amount=paid_amount,
        balance=balance,
        adults=data.get('adults', 1),
        children=data.get('children', 0),
        source=data.get('source'),
        booking_agent=data.get('booking_agent'),
        board_type=data.get('board_type'),
        special_requests=data.get('special_requests'),
        notes=data.get('notes'),
        created_by_id=current_user.id,
    )

    if room_id:
        Room.objects.filter(id=room_id).update(status=RoomStatusEnum.RESERVED)

    from api.services.audit import write_audit
    write_audit(
        reservation.tenant,
        current_user,
        'create',
        'reservation',
        reservation.id,
        reservation.reservation_number,
        f'{guest.first_name} {guest.last_name}',
    )

    return Response({
        'message': 'Reservation created successfully',
        'reservation': {
            'id': reservation.id,
            'reservation_number': reservation.reservation_number,
            'guest_name': f'{guest.first_name} {guest.last_name}',
            'check_in_date': reservation.check_in_date.isoformat(),
            'check_out_date': reservation.check_out_date.isoformat(),
            'nights': nights,
            'total_amount': float(total_amount),
            'balance': float(balance),
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_guests(request):
    """Search for existing guests."""
    current_user = request.user
    denied = deny_if_no_tenant(current_user)
    if denied:
        return denied

    query = request.query_params.get('query', '')
    limit = int(request.query_params.get('limit', 10))
    tenant_id = current_user.tenant_id

    guests = Guest.objects.filter(
        tenant_id=tenant_id,
    ).filter(
        Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
        | Q(email__icontains=query)
        | Q(phone__icontains=query)
        | Q(id_number__icontains=query)
    )[:limit]

    return Response({
        'guests': [
            {
                'id': g.id,
                'name': f'{g.first_name} {g.last_name}',
                'email': g.email,
                'phone': g.phone,
                'is_vip': g.is_vip,
                'loyalty_points': g.loyalty_points,
            }
            for g in guests
        ],
    })


def _serialize_guest_row(g):
    return {
        'id': g.id,
        'first_name': g.first_name,
        'last_name': g.last_name,
        'name': g.full_name,
        'email': g.email or '',
        'phone': g.phone or g.mobile or '',
        'nationality': g.nationality or '',
        'id_number': g.id_number or '',
        'is_vip': 'Yes' if g.is_vip else 'No',
        'loyalty_points': g.loyalty_points,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def guests(request):
    """Comprehensive guest list (GYOROOM customer details)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant_id = request.user.tenant_id
    if request.method == 'POST':
        data = request.data or {}
        first = (data.get('first_name') or '').strip()
        last = (data.get('last_name') or '').strip()
        if not first:
            return Response({'detail': 'first_name is required'}, status=status.HTTP_400_BAD_REQUEST)
        guest = Guest.objects.create(
            tenant_id=tenant_id,
            first_name=first,
            last_name=last or '-',
            email=data.get('email') or None,
            phone=data.get('phone') or None,
            nationality=data.get('nationality') or None,
            id_number=data.get('id_number') or None,
            notes=data.get('notes') or None,
        )
        return Response(_serialize_guest_row(guest), status=status.HTTP_201_CREATED)
    qs = Guest.objects.filter(tenant_id=tenant_id).order_by('-created_at')
    q = (request.query_params.get('query') or '').strip()
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
            | Q(id_number__icontains=q)
        )
    return Response({'items': [_serialize_guest_row(g) for g in qs[:300]]})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_rooms(request):
    """Get available rooms for given dates."""
    current_user = request.user
    denied = deny_if_no_tenant(current_user)
    if denied:
        return denied

    check_in = request.query_params.get('check_in')
    check_out = request.query_params.get('check_out')
    room_type_id = request.query_params.get('room_type_id')
    tenant = current_user.tenant
    if not tenant:
        return Response({'rooms': [], 'total': 0})

    try:
        check_in_date = parse_datetime(check_in, hotel_check_in=True)
        check_out_date = parse_datetime(check_out, hotel_check_out=True)
    except (ValueError, AttributeError):
        return Response({'detail': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

    qs = available_rooms_qs(tenant, check_in_date, check_out_date, room_type_id)
    available_rooms_list = list(qs.order_by('room_number'))

    return Response({
        'rooms': [
            {
                'id': room.id,
                'room_number': room.room_number,
                'floor': room.floor,
                'room_type': {
                    'id': room.room_type.id,
                    'name': room.room_type.name,
                    'base_rate': float(room.room_type.base_rate) if room.room_type.base_rate else None,
                },
                'rack_rate': float(room.rack_rate) if room.rack_rate else None,
                'bed_type': room.bed_type,
                'view': room.view,
            }
            for room in available_rooms_list
        ],
        'total': len(available_rooms_list),
    })
