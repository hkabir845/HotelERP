"""Assets & Maintenance endpoints."""
import uuid
from datetime import datetime, timedelta

from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.views import deny_if_no_tenant


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assets_list(request):
    """Get assets (mock data)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied

    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')

    assets = [
        {'id': 1, 'asset_code': f"AST-{str(uuid.uuid4())[:8].upper()}", 'name': 'Air Conditioning Unit - Room 101', 'category': 'HVAC', 'type': 'Split AC', 'purchase_date': (datetime.now() - timedelta(days=365)).isoformat(), 'purchase_cost': 2500.00, 'current_value': 2000.00, 'location': 'Room 101', 'status': 'active', 'depreciation_rate': 20.0},
        {'id': 2, 'asset_code': f"AST-{str(uuid.uuid4())[:8].upper()}", 'name': 'Commercial Refrigerator', 'category': 'Kitchen Equipment', 'type': 'Refrigerator', 'purchase_date': (datetime.now() - timedelta(days=730)).isoformat(), 'purchase_cost': 5000.00, 'current_value': 3500.00, 'location': 'Kitchen', 'status': 'active', 'depreciation_rate': 15.0},
        {'id': 3, 'asset_code': f"AST-{str(uuid.uuid4())[:8].upper()}", 'name': 'Elevator Motor', 'category': 'Building Systems', 'type': 'Motor', 'purchase_date': (datetime.now() - timedelta(days=180)).isoformat(), 'purchase_cost': 8000.00, 'current_value': 7500.00, 'location': 'Elevator Shaft', 'status': 'maintenance', 'depreciation_rate': 10.0},
    ]

    filtered = assets
    if status_filter and status_filter != 'all':
        filtered = [a for a in filtered if a['status'] == status_filter]
    if search:
        filtered = [
            a for a in filtered
            if search.lower() in a['asset_code'].lower()
            or search.lower() in a['name'].lower()
            or search.lower() in a['location'].lower()
        ]

    return Response({'assets': filtered})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def maintenance_requests(request):
    """Get maintenance requests (mock data)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied

    current_user = request.user
    status_filter = request.query_params.get('status')
    priority = request.query_params.get('priority')
    search = request.query_params.get('search')

    requests_list = [
        {'id': 1, 'request_number': f"MR-{str(uuid.uuid4())[:8].upper()}", 'asset_name': 'Air Conditioning Unit - Room 101', 'asset_code': 'AST-ABC123', 'location': 'Room 101', 'requested_by': current_user.first_name + ' ' + current_user.last_name, 'priority': 'urgent', 'status': 'pending', 'issue_description': 'AC not cooling properly', 'requested_date': datetime.now().isoformat(), 'assigned_to': None, 'completed_date': None},
        {'id': 2, 'request_number': f"MR-{str(uuid.uuid4())[:8].upper()}", 'asset_name': 'Commercial Refrigerator', 'asset_code': 'AST-DEF456', 'location': 'Kitchen', 'requested_by': 'Kitchen Staff', 'priority': 'high', 'status': 'in_progress', 'issue_description': 'Temperature fluctuation', 'requested_date': (datetime.now() - timedelta(days=2)).isoformat(), 'assigned_to': 'Maintenance Team', 'completed_date': None},
        {'id': 3, 'request_number': f"MR-{str(uuid.uuid4())[:8].upper()}", 'asset_name': 'Elevator Motor', 'asset_code': 'AST-GHI789', 'location': 'Elevator Shaft', 'requested_by': 'Building Manager', 'priority': 'urgent', 'status': 'completed', 'issue_description': 'Routine maintenance', 'requested_date': (datetime.now() - timedelta(days=5)).isoformat(), 'assigned_to': 'Maintenance Team', 'completed_date': datetime.now().isoformat()},
    ]

    filtered = requests_list
    if status_filter and status_filter != 'all':
        filtered = [r for r in filtered if r['status'] == status_filter]
    if priority and priority != 'all':
        filtered = [r for r in filtered if r['priority'] == priority]
    if search:
        filtered = [
            r for r in filtered
            if search.lower() in r['request_number'].lower()
            or search.lower() in r['asset_name'].lower()
            or search.lower() in r['location'].lower()
        ]

    return Response({'requests': filtered})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def work_orders(request):
    """Get work orders (mock data)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied

    status_filter = request.query_params.get('status')
    priority = request.query_params.get('priority')
    search = request.query_params.get('search')

    work_orders_list = [
        {'id': 1, 'work_order_number': f"WO-{str(uuid.uuid4())[:8].upper()}", 'maintenance_request_id': 1, 'asset_name': 'Air Conditioning Unit - Room 101', 'location': 'Room 101', 'assigned_to': 'Maintenance Team', 'priority': 'urgent', 'status': 'in_progress', 'estimated_cost': 500.00, 'actual_cost': None, 'scheduled_date': datetime.now().isoformat(), 'started_date': datetime.now().isoformat(), 'completed_date': None, 'description': 'AC repair and maintenance'},
        {'id': 2, 'work_order_number': f"WO-{str(uuid.uuid4())[:8].upper()}", 'maintenance_request_id': 2, 'asset_name': 'Commercial Refrigerator', 'location': 'Kitchen', 'assigned_to': 'Maintenance Team', 'priority': 'high', 'status': 'approved', 'estimated_cost': 800.00, 'actual_cost': None, 'scheduled_date': (datetime.now().replace(day=datetime.now().day + 2)).isoformat(), 'started_date': None, 'completed_date': None, 'description': 'Temperature control system repair'},
        {'id': 3, 'work_order_number': f"WO-{str(uuid.uuid4())[:8].upper()}", 'maintenance_request_id': 3, 'asset_name': 'Elevator Motor', 'location': 'Elevator Shaft', 'assigned_to': 'Maintenance Team', 'priority': 'medium', 'status': 'completed', 'estimated_cost': 1200.00, 'actual_cost': 1150.00, 'scheduled_date': (datetime.now().replace(day=datetime.now().day - 5)).isoformat(), 'started_date': (datetime.now().replace(day=datetime.now().day - 5)).isoformat(), 'completed_date': datetime.now().isoformat(), 'description': 'Routine maintenance completed'},
    ]

    filtered = work_orders_list
    if status_filter and status_filter != 'all':
        filtered = [wo for wo in filtered if wo['status'] == status_filter]
    if priority and priority != 'all':
        filtered = [wo for wo in filtered if wo['priority'] == priority]
    if search:
        filtered = [
            wo for wo in filtered
            if search.lower() in wo['work_order_number'].lower()
            or search.lower() in wo['asset_name'].lower()
            or search.lower() in wo['location'].lower()
        ]

    return Response({'work_orders': filtered})


def _tenant(request):
    return getattr(request.user, 'tenant', None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def depreciation(request):
    from datetime import date as date_cls
    from api.models import Asset

    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    today = date_cls.today()
    rows = []
    total_cost = 0
    total_accum = 0
    total_value = 0
    for asset in Asset.objects.filter(tenant=tenant).select_related('category').order_by('asset_code'):
        cost = float(asset.purchase_price or 0)
        rate = float(asset.depreciation_rate or asset.category.depreciation_rate or 0)
        years = 0
        if asset.purchase_date:
            years = max(0, (today - asset.purchase_date).days / 365.25)
        accum = float(asset.accumulated_depreciation or 0)
        if not accum and cost and rate:
            accum = min(cost, cost * (rate / 100.0) * years)
        value = float(asset.current_value) if asset.current_value is not None else max(0, cost - accum)
        total_cost += cost
        total_accum += accum
        total_value += value
        rows.append({
            'code': asset.asset_code,
            'name': asset.name,
            'category': asset.category.name if asset.category_id else '',
            'purchase_date': asset.purchase_date.isoformat() if asset.purchase_date else '',
            'cost': round(cost, 2),
            'rate': round(rate, 2),
            'accumulated': round(accum, 2),
            'current_value': round(value, 2),
        })
    return Response({
        'kind': 'depreciation',
        'title': 'Asset Depreciation',
        'columns': ['Code', 'Name', 'Category', 'Purchased', 'Cost', 'Rate %', 'Accumulated', 'Book value'],
        'rows': [
            [r['code'], r['name'], r['category'], r['purchase_date'], r['cost'], r['rate'], r['accumulated'], r['current_value']]
            for r in rows
        ],
        'summary': {
            'assets': len(rows),
            'purchase_cost': round(total_cost, 2),
            'accumulated': round(total_accum, 2),
            'book_value': round(total_value, 2),
        },
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def maintenance_schedules(request):
    from datetime import datetime
    from api.models import Asset, MaintenanceSchedule

    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    assets = Asset.objects.filter(tenant=tenant).order_by('asset_code')
    if request.method == 'POST':
        data = request.data or {}
        asset = Asset.objects.filter(tenant=tenant, id=data.get('asset_id')).first()
        title = (data.get('title') or '').strip()
        due = data.get('next_due_date')
        if not asset or not title or not due:
            return Response({'detail': 'Asset, title, and next due date are required'}, status=400)
        due_date = datetime.strptime(str(due)[:10], '%Y-%m-%d').date()
        row = MaintenanceSchedule.objects.create(
            tenant=tenant,
            asset=asset,
            title=title,
            description=data.get('description') or data.get('notes') or '',
            frequency_type=(data.get('frequency_type') or 'months'),
            frequency_value=int(data.get('frequency_value') or 1),
            next_due_date=due_date,
        )
        return Response({'id': row.id, 'title': row.title}, status=201)
    items = [
        {
            'id': row.id,
            'asset_code': row.asset.asset_code,
            'asset_name': row.asset.name,
            'title': row.title,
            'frequency': f'{row.frequency_value} {row.frequency_type}',
            'next_due_date': row.next_due_date.isoformat() if row.next_due_date else '',
            'last_performed': row.last_performed.isoformat() if row.last_performed else '',
            'is_active': row.is_active,
        }
        for row in MaintenanceSchedule.objects.filter(tenant=tenant).select_related('asset').order_by('next_due_date')
    ]
    return Response({
        'items': items,
        'options': {
            'assets': [{'id': a.id, 'name': f'{a.asset_code} {a.name}'} for a in assets],
            'frequencies': [
                {'id': 'days', 'name': 'Days'},
                {'id': 'weeks', 'name': 'Weeks'},
                {'id': 'months', 'name': 'Months'},
                {'id': 'years', 'name': 'Years'},
            ],
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def maintenance_history(request):
    from api.models import MaintenanceRequest, MaintenanceStatus

    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    qs = MaintenanceRequest.objects.filter(
        tenant=tenant,
        status=MaintenanceStatus.COMPLETED,
    ).select_related('asset').order_by('-completed_at', '-id')
    rows = []
    for row in qs[:300]:
        rows.append([
            row.request_number,
            row.asset.name if row.asset_id else '',
            row.title,
            row.maintenance_type,
            row.completed_at.date().isoformat() if row.completed_at else '',
            float(row.actual_cost or 0),
            row.work_performed or row.resolution_notes or '',
        ])
    return Response({
        'kind': 'maintenance-history',
        'title': 'Maintenance History',
        'columns': ['Request', 'Asset', 'Title', 'Type', 'Completed', 'Cost', 'Work performed'],
        'rows': rows,
        'summary': {'completed': len(rows)},
    })
