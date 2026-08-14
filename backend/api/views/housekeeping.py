"""Housekeeping endpoints."""
import uuid
from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import HousekeepingTask, Room, RoomStatus, RoomStatusEnum, RoomType, TaskStatus
from api.views import deny_if_no_tenant


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wake_up_calls(request):
    """Get wake-up calls (mock data)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied

    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')

    calls = [
        {
            'id': 1,
            'room_number': '101',
            'guest_name': 'John Doe',
            'wake_up_time': datetime.now().replace(hour=7, minute=0, second=0, microsecond=0).isoformat(),
            'status': 'scheduled',
            'completed_at': None,
            'notes': 'Early morning flight',
        },
        {
            'id': 2,
            'room_number': '205',
            'guest_name': 'Jane Smith',
            'wake_up_time': datetime.now().replace(hour=8, minute=30, second=0, microsecond=0).isoformat(),
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'notes': None,
        },
    ]

    filtered = calls
    if status_filter and status_filter != 'all':
        filtered = [c for c in filtered if c['status'] == status_filter]
    if search:
        filtered = [
            c for c in filtered
            if search.lower() in c['room_number'].lower()
            or search.lower() in c['guest_name'].lower()
        ]

    return Response({'calls': filtered})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lost_found(request):
    """Get lost & found items (mock data)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied

    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')

    items = [
        {
            'id': 1,
            'item_number': f"LF-{str(uuid.uuid4())[:8].upper()}",
            'item_name': 'Mobile Phone',
            'description': 'Black iPhone 13',
            'location_found': 'Lobby',
            'room_number': None,
            'guest_name': None,
            'status': 'found',
            'found_date': datetime.now().isoformat(),
            'claimed_date': None,
            'category': 'Electronics',
        },
        {
            'id': 2,
            'item_number': f"LF-{str(uuid.uuid4())[:8].upper()}",
            'item_name': 'Wallet',
            'description': 'Brown leather wallet with credit cards',
            'location_found': 'Restaurant',
            'room_number': '101',
            'guest_name': 'John Doe',
            'status': 'claimed',
            'found_date': (datetime.now().replace(day=datetime.now().day - 2)).isoformat(),
            'claimed_date': datetime.now().isoformat(),
            'category': 'Personal Items',
        },
    ]

    filtered = items
    if status_filter and status_filter != 'all':
        filtered = [i for i in filtered if i['status'] == status_filter]
    if search:
        filtered = [
            i for i in filtered
            if search.lower() in i['item_name'].lower()
            or search.lower() in (i.get('room_number') or '').lower()
            or search.lower() in (i.get('guest_name') or '').lower()
        ]

    return Response({'items': filtered})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks(request):
    """Get housekeeping tasks."""
    current_user = request.user
    denied = deny_if_no_tenant(current_user)
    if denied:
        return denied

    tenant_id = current_user.tenant_id
    status_filter = request.query_params.get('status')
    priority = request.query_params.get('priority')
    search = request.query_params.get('search')

    qs = HousekeepingTask.objects.select_related('room', 'room__room_type', 'assigned_to')
    if tenant_id:
        qs = qs.filter(tenant_id=tenant_id)

    if status_filter:
        if status_filter in TaskStatus.values:
            qs = qs.filter(status=status_filter)

    if priority:
        from api.models import TaskPriority
        if priority in TaskPriority.values:
            qs = qs.filter(priority=priority)

    if search:
        qs = qs.filter(
            Q(room__room_number__icontains=search) | Q(description__icontains=search)
        )

    result = []
    for task in qs.order_by('-scheduled_date'):
        result.append({
            'id': task.id,
            'task_number': f'TASK-{task.id}',
            'room': {
                'id': task.room.id,
                'room_number': task.room.room_number,
                'room_type': task.room.room_type.name,
            },
            'task_type': task.task_type,
            'status': task.status,
            'priority': task.priority,
            'assigned_to': {
                'id': task.assigned_to.id,
                'name': f'{task.assigned_to.first_name} {task.assigned_to.last_name}',
            } if task.assigned_to else None,
            'scheduled_date': task.scheduled_date.isoformat() if task.scheduled_date else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'description': task.description,
        })

    return Response({'tasks': result})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_status_list(request):
    """Get all rooms with their status for housekeeping."""
    current_user = request.user
    status_filter = request.query_params.get('status')
    floor = request.query_params.get('floor')
    room_type_id = request.query_params.get('room_type_id')
    search = request.query_params.get('search')

    qs = Room.objects.select_related('room_type')
    if current_user.tenant_id:
        qs = qs.filter(tenant_id=current_user.tenant_id)
    elif not current_user.is_superuser:
        return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    if status_filter and status_filter in RoomStatusEnum.values:
        qs = qs.filter(status=status_filter)

    if floor is not None:
        try:
            qs = qs.filter(floor=int(floor))
        except ValueError:
            pass

    if room_type_id:
        qs = qs.filter(room_type_id=room_type_id)

    if search:
        qs = qs.filter(
            Q(room_number__icontains=search) | Q(room_type__name__icontains=search)
        )

    rooms = list(qs.order_by('floor', 'room_number'))
    room_ids = [room.id for room in rooms]

    tasks = HousekeepingTask.objects.filter(
        room_id__in=room_ids,
        status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
    )
    tasks_by_room = {task.room_id: task for task in tasks}

    room_statuses = RoomStatus.objects.filter(room_id__in=room_ids)
    status_by_room = {rs.room_id: rs for rs in room_statuses}

    result = []
    for room in rooms:
        room_status = status_by_room.get(room.id)
        task = tasks_by_room.get(room.id)
        result.append({
            'id': room.id,
            'room_number': room.room_number,
            'floor': room.floor,
            'room_type': {
                'id': room.room_type.id,
                'name': room.room_type.name,
                'max_occupancy': room.room_type.max_occupancy,
            },
            'status': room.status,
            'bed_type': room.bed_type,
            'view': room.view,
            'housekeeping_status': room_status.housekeeping_status if room_status else None,
            'last_cleaned': room_status.last_cleaned.isoformat() if room_status and room_status.last_cleaned else None,
            'last_inspected': room_status.last_inspected.isoformat() if room_status and room_status.last_inspected else None,
            'next_cleaning_due': room_status.next_cleaning_due.isoformat() if room_status and room_status.next_cleaning_due else None,
            'has_pending_task': task is not None,
            'task_type': task.task_type if task else None,
            'task_status': task.status if task else None,
            'notes': room_status.notes if room_status else room.notes,
            'is_active': room.is_active,
        })

    return Response({
        'rooms': result,
        'total': len(result),
        'summary': {
            'available': len([r for r in result if r['status'] == 'available']),
            'occupied': len([r for r in result if r['status'] == 'occupied']),
            'cleaning': len([r for r in result if r['status'] == 'cleaning']),
            'maintenance': len([r for r in result if r['status'] == 'maintenance']),
            'out_of_order': len([r for r in result if r['status'] == 'out_of_order']),
            'reserved': len([r for r in result if r['status'] == 'reserved']),
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def floors(request):
    """Get list of floors."""
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
    """Get list of room types."""
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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_room_status(request, room_id):
    """Update room status."""
    current_user = request.user
    status_value = request.query_params.get('status')
    housekeeping_status = request.query_params.get('housekeeping_status')
    notes = request.query_params.get('notes')

    if not status_value:
        return Response({'detail': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({'detail': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

    if current_user.tenant_id and room.tenant_id != current_user.tenant_id:
        return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    if status_value not in RoomStatusEnum.values:
        return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    room.status = status_value
    room.save(update_fields=['status'])

    room_status, _created = RoomStatus.objects.get_or_create(
        room_id=room_id,
        defaults={
            'tenant_id': room.tenant_id,
            'status': status_value,
            'housekeeping_status': housekeeping_status or 'dirty',
        },
    )
    if not _created:
        room_status.status = status_value
        if housekeeping_status:
            room_status.housekeeping_status = housekeeping_status
        if notes:
            room_status.notes = notes
        room_status.updated_by = current_user
        room_status.save()

    return Response({
        'message': 'Room status updated successfully',
        'room_id': room_id,
        'status': status_value,
    })
