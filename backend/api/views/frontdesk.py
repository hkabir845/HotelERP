"""Frontdesk endpoints."""
from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import Guest, Reservation, ReservationStatus, Room, RoomStatusEnum, RoomType


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_rack(request):
    """Get room rack data for front desk display."""
    current_user = request.user
    floor = request.query_params.get('floor')
    room_type_id = request.query_params.get('room_type_id')
    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')
    date_filter = request.query_params.get('date_filter')

    qs = Room.objects.select_related('room_type')
    if current_user.tenant_id:
        qs = qs.filter(tenant_id=current_user.tenant_id)
    elif not current_user.is_superuser:
        return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    if floor is not None:
        try:
            qs = qs.filter(floor=int(floor))
        except ValueError:
            pass

    if room_type_id:
        qs = qs.filter(room_type_id=room_type_id)

    if status_filter and status_filter in RoomStatusEnum.values:
        qs = qs.filter(status=status_filter)

    if search:
        qs = qs.filter(
            Q(room_number__icontains=search) | Q(room_type__name__icontains=search)
        )

    rooms = list(qs.order_by('floor', 'room_number'))
    room_ids = [room.id for room in rooms]

    filter_date = datetime.now().date()
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        except ValueError:
            pass

    filter_datetime_start = datetime.combine(filter_date, datetime.min.time())
    filter_datetime_end = datetime.combine(filter_date, datetime.max.time())

    reservations = Reservation.objects.select_related('guest').filter(
        room_id__in=room_ids,
        status__in=[
            ReservationStatus.CONFIRMED,
            ReservationStatus.CHECKED_IN,
            ReservationStatus.PENDING,
        ],
        check_in_date__lte=filter_datetime_end,
        check_out_date__gt=filter_datetime_start,
    )

    reservations_by_room = {}
    for reservation in reservations:
        if reservation.room_id:
            reservations_by_room.setdefault(reservation.room_id, []).append(reservation)

    result = []
    for room in rooms:
        room_reservations = reservations_by_room.get(room.id, [])
        current_reservation = None
        for res in room_reservations:
            if res.status == ReservationStatus.CHECKED_IN:
                current_reservation = res
                break
            elif res.status == ReservationStatus.CONFIRMED and not current_reservation:
                current_reservation = res

        if not current_reservation and room_reservations:
            current_reservation = room_reservations[0]

        result.append({
            'id': room.id,
            'room_number': room.room_number,
            'floor': room.floor,
            'room_type': {
                'id': room.room_type.id,
                'name': room.room_type.name,
                'max_occupancy': room.room_type.max_occupancy,
                'base_rate': float(room.room_type.base_rate) if room.room_type.base_rate else None,
            },
            'status': room.status,
            'bed_type': room.bed_type,
            'view': room.view,
            'rack_rate': float(room.rack_rate) if room.rack_rate else None,
            'is_active': room.is_active,
            'current_reservation': {
                'id': current_reservation.id,
                'reservation_number': current_reservation.reservation_number,
                'guest': {
                    'id': current_reservation.guest.id,
                    'name': f'{current_reservation.guest.first_name} {current_reservation.guest.last_name}',
                    'first_name': current_reservation.guest.first_name,
                    'last_name': current_reservation.guest.last_name,
                    'phone': current_reservation.guest.phone,
                    'email': current_reservation.guest.email,
                    'is_vip': current_reservation.guest.is_vip,
                },
                'check_in_date': current_reservation.check_in_date.isoformat() if current_reservation.check_in_date else None,
                'check_out_date': current_reservation.check_out_date.isoformat() if current_reservation.check_out_date else None,
                'actual_check_in': current_reservation.actual_check_in.isoformat() if current_reservation.actual_check_in else None,
                'actual_check_out': current_reservation.actual_check_out.isoformat() if current_reservation.actual_check_out else None,
                'status': current_reservation.status,
                'reservation_type': current_reservation.reservation_type,
                'adults': current_reservation.adults,
                'children': current_reservation.children,
                'room_rate': float(current_reservation.room_rate) if current_reservation.room_rate else None,
                'total_amount': float(current_reservation.total_amount) if current_reservation.total_amount else None,
                'paid_amount': float(current_reservation.paid_amount) if current_reservation.paid_amount else None,
                'balance': float(current_reservation.balance) if current_reservation.balance else None,
                'source': current_reservation.source,
                'nights': (
                    (current_reservation.check_out_date - current_reservation.check_in_date).days
                    if current_reservation.check_in_date and current_reservation.check_out_date else 0
                ),
            } if current_reservation else None,
            'all_reservations': [
                {
                    'id': res.id,
                    'reservation_number': res.reservation_number,
                    'guest_name': f'{res.guest.first_name} {res.guest.last_name}',
                    'check_in_date': res.check_in_date.isoformat() if res.check_in_date else None,
                    'check_out_date': res.check_out_date.isoformat() if res.check_out_date else None,
                    'status': res.status,
                    'nights': (
                        (res.check_out_date - res.check_in_date).days
                        if res.check_in_date and res.check_out_date else 0
                    ),
                }
                for res in room_reservations
            ],
        })

    return Response({
        'rooms': result,
        'total': len(result),
        'summary': {
            'available': len([r for r in result if r['status'] == 'available' and not r['current_reservation']]),
            'occupied': len([r for r in result if r['status'] == 'occupied' or r['current_reservation']]),
            'reserved': len([r for r in result if r['status'] == 'reserved']),
            'out_of_order': len([r for r in result if r['status'] == 'out_of_order']),
            'maintenance': len([r for r in result if r['status'] == 'maintenance']),
            'cleaning': len([r for r in result if r['status'] == 'cleaning']),
        },
        'filter_date': filter_date.isoformat(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def floors(request):
    """Get list of floors for filtering."""
    current_user = request.user
    qs = Room.objects.values_list('floor', flat=True).distinct()

    if current_user.tenant_id:
        qs = qs.filter(tenant_id=current_user.tenant_id)
    elif not current_user.is_superuser:
        return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    floors_list = sorted({f for f in qs if f is not None})
    return Response({'floors': floors_list})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_types(request):
    """Get list of room types for filtering."""
    current_user = request.user
    qs = RoomType.objects.filter(is_active=True)

    if current_user.tenant_id:
        qs = qs.filter(tenant_id=current_user.tenant_id)
    elif not current_user.is_superuser:
        return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    return Response({
        'room_types': [
            {
                'id': rt.id,
                'name': rt.name,
                'description': rt.description,
                'max_occupancy': rt.max_occupancy,
            }
            for rt in qs
        ],
    })
