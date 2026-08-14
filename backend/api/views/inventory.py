"""Inventory masters, stock movements, supplier payments, and reports."""
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    InventoryCategory,
    InventoryItem,
    InventoryMovement,
    InventoryStock,
    InventoryUnit,
    Purchase,
    PurchaseItem,
    PurchaseStatus,
    Requisition,
    RequisitionItem,
    RequisitionStatus,
    RevenueCenter,
    StockAdjustment,
    StockAdjustmentItem,
    StockConsumption,
    StockConsumptionItem,
    Supplier,
    SupplierPayment,
    Warehouse,
    WarehouseTransfer,
    WarehouseTransferItem,
)
from api.views import deny_if_no_tenant


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _dec(value, default='0'):
    if value in (None, ''):
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value in (None, ''):
        return default
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def _date(value):
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()


def _fk(model, tenant, pk):
    if not pk:
        return None
    try:
        return model.objects.get(id=int(pk), tenant=tenant)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _opt(qs):
    return [{'id': row.id, 'name': getattr(row, 'name', str(row.id))} for row in qs]


def _money(value):
    return float(value or 0)


def _uname(user):
    if not user:
        return 'Unknown'
    full = f'{user.first_name or ""} {user.last_name or ""}'.strip()
    return full or user.username or user.email or 'Unknown'


def _num(model, tenant, prefix):
    n = model.objects.filter(tenant=tenant).count() + 1
    return f'{prefix}-{tenant.id}-{n:05d}'


def _seed(tenant):
    if not Warehouse.objects.filter(tenant=tenant).exists():
        Warehouse.objects.create(tenant=tenant, name='Main Store', location='Stores')
        Warehouse.objects.create(tenant=tenant, name='Housekeeping', location='HK')
    if not InventoryUnit.objects.filter(tenant=tenant).exists():
        for name in ('Pcs', 'Kg', 'Litre', 'Bottle'):
            InventoryUnit.objects.create(tenant=tenant, name=name)
    if not InventoryCategory.objects.filter(tenant=tenant).exists():
        for name in ('Housekeeping', 'Kitchen', 'Amenities'):
            InventoryCategory.objects.create(tenant=tenant, name=name)
    if not InventoryItem.objects.filter(tenant=tenant).exists():
        wh = Warehouse.objects.filter(tenant=tenant).first()
        cat = InventoryCategory.objects.filter(tenant=tenant, name='Housekeeping').first()
        InventoryItem.objects.create(
            tenant=tenant,
            item_code=f'ITM-{tenant.id}-00001',
            name='Toilet Paper',
            unit='Pcs',
            category=cat,
            warehouse=wh,
            min_stock_level=20,
            cost_price=Decimal('1.50'),
        )
        InventoryItem.objects.create(
            tenant=tenant,
            item_code=f'ITM-{tenant.id}-00002',
            name='Bath Soap',
            unit='Pcs',
            category=cat,
            warehouse=wh,
            min_stock_level=30,
            cost_price=Decimal('0.80'),
        )


def _options(tenant):
    _seed(tenant)
    centers = _opt(RevenueCenter.objects.filter(tenant=tenant, is_active=True).order_by('name'))
    if not centers:
        centers = [{'id': n, 'name': n} for n in ('Restaurant', 'Room Service', 'Banquet', 'Housekeeping')]
    return {
        'categories': _opt(InventoryCategory.objects.filter(tenant=tenant).order_by('name')),
        'units': _opt(InventoryUnit.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'warehouses': _opt(Warehouse.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'items': [
            {
                'id': row.id,
                'name': f'{row.item_code} — {row.name}',
                'item_name': row.name,
                'unit': row.unit,
                'cost_price': _money(row.cost_price),
            }
            for row in InventoryItem.objects.filter(tenant=tenant, is_active=True).order_by('name')[:400]
        ],
        'suppliers': _opt(Supplier.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'revenue_centers': centers,
        'payment_methods': [
            {'id': 'cash', 'name': 'Cash'},
            {'id': 'bank', 'name': 'Bank'},
            {'id': 'card', 'name': 'Card'},
            {'id': 'mobile', 'name': 'Mobile'},
        ],
    }


def _stock_qty(item, warehouse):
    if not warehouse:
        return Decimal('0')
    row = InventoryStock.objects.filter(item=item, warehouse=warehouse).first()
    return row.quantity if row else Decimal('0')


def _move(tenant, item, warehouse, qty, unit_cost, ref_type, ref_id, ref_number, day, user=None, notes=''):
    qty = Decimal(str(qty))
    if qty == 0:
        return
    if not warehouse:
        raise ValueError('Warehouse is required')
    stock, _ = InventoryStock.objects.get_or_create(
        tenant=tenant,
        item=item,
        warehouse=warehouse,
        defaults={'quantity': Decimal('0')},
    )
    new_qty = (stock.quantity or Decimal('0')) + qty
    if new_qty < 0:
        raise ValueError(f'Insufficient stock of {item.name} in {warehouse.name}')
    old_on_hand = item.current_stock or Decimal('0')
    old_cost = item.cost_price or Decimal('0')
    if qty > 0 and unit_cost is not None:
        incoming = Decimal(str(unit_cost))
        denom = old_on_hand + qty
        if denom > 0:
            item.cost_price = ((old_on_hand * old_cost) + (qty * incoming)) / denom
    stock.quantity = new_qty
    stock.save()
    InventoryMovement.objects.create(
        tenant=tenant,
        item=item,
        warehouse=warehouse,
        movement_date=day,
        quantity=qty,
        unit_cost=unit_cost or 0,
        ref_type=ref_type,
        ref_id=ref_id,
        ref_number=ref_number,
        notes=notes or '',
        created_by=user,
    )
    total = InventoryStock.objects.filter(item=item).aggregate(s=Sum('quantity'))['s'] or Decimal('0')
    item.current_stock = total
    item.save(update_fields=['current_stock', 'cost_price', 'updated_at'])


def serialize_named(row):
    data = {
        'id': row.id,
        'name': row.name,
        'description': getattr(row, 'description', None) or '',
        'is_active': getattr(row, 'is_active', True),
    }
    if hasattr(row, 'location'):
        data['location'] = row.location or ''
    if hasattr(row, 'contact_person'):
        data['contact_person'] = row.contact_person or ''
        data['phone'] = row.phone or ''
        data['email'] = row.email or ''
        data['address'] = row.address or ''
        data['due_balance'] = _money(_supplier_due(row))
    return data


def serialize_item(row):
    return {
        'id': row.id,
        'name': row.name,
        'item_code': row.item_code,
        'description': row.description or '',
        'category_id': row.category_id,
        'category_name': row.category.name if row.category_id else '',
        'unit': row.unit or '',
        'warehouse_id': row.warehouse_id,
        'warehouse_name': row.warehouse.name if row.warehouse_id else '',
        'supplier_id': row.supplier_id,
        'current_stock': _money(row.current_stock),
        'min_stock_level': _money(row.min_stock_level),
        'cost_price': _money(row.cost_price),
        'selling_price': _money(row.selling_price) if row.selling_price is not None else None,
        'is_active': row.is_active,
    }


def _lines_payload(qs):
    rows = []
    for line in qs:
        rows.append({
            'id': line.id,
            'item_id': line.item_id,
            'item_name': line.item.name if line.item_id else '',
            'item_code': line.item.item_code if line.item_id else '',
            'unit': getattr(line, 'unit', None) or (line.item.unit if line.item_id else ''),
            'quantity': _money(line.quantity),
            'unit_price': _money(getattr(line, 'unit_price', None) or getattr(line, 'unit_cost', 0)),
            'total_price': _money(getattr(line, 'total_price', None) or getattr(line, 'total_cost', 0)),
        })
    return rows


def serialize_requisition(row):
    return {
        'id': row.id,
        'number': row.requisition_number,
        'department': row.department or '',
        'warehouse_id': row.warehouse_id,
        'warehouse_name': row.warehouse.name if row.warehouse_id else '',
        'status': row.status,
        'requested_date': row.requested_date.isoformat() if row.requested_date else None,
        'required_date': row.required_date.isoformat() if row.required_date else None,
        'notes': row.notes or '',
        'requested_by': _uname(row.requested_by),
        'items': _lines_payload(row.items.select_related('item').all()),
        'can_post': row.status == RequisitionStatus.APPROVED,
        'can_edit': row.status == RequisitionStatus.PENDING,
    }


def serialize_purchase(row):
    paid = row.paid_amount or Decimal('0')
    total = row.total_amount or Decimal('0')
    signed = -total if row.is_return else total
    return {
        'id': row.id,
        'number': row.purchase_number,
        'is_return': row.is_return,
        'supplier_id': row.supplier_id,
        'supplier_name': row.supplier.name if row.supplier_id else '',
        'warehouse_id': row.warehouse_id,
        'warehouse_name': row.warehouse.name if row.warehouse_id else '',
        'purchase_date': row.purchase_date.isoformat() if row.purchase_date else None,
        'status': row.status,
        'subtotal': _money(row.subtotal),
        'tax_amount': _money(row.tax_amount),
        'discount': _money(row.discount),
        'total_amount': _money(total),
        'paid_amount': _money(paid),
        'due': _money(signed - paid) if not row.is_return else 0,
        'notes': row.notes or '',
        'items': _lines_payload(row.items.select_related('item').all()),
        'can_post': row.status in (PurchaseStatus.DRAFT, PurchaseStatus.PENDING),
        'can_edit': row.status in (PurchaseStatus.DRAFT, PurchaseStatus.PENDING),
    }


def serialize_transfer(row):
    return {
        'id': row.id,
        'number': row.transfer_number,
        'from_warehouse_id': row.from_warehouse_id,
        'from_warehouse_name': row.from_warehouse.name if row.from_warehouse_id else '',
        'to_warehouse_id': row.to_warehouse_id,
        'to_warehouse_name': row.to_warehouse.name if row.to_warehouse_id else '',
        'transfer_date': row.transfer_date.isoformat() if row.transfer_date else None,
        'status': row.status,
        'notes': row.notes or '',
        'items': _lines_payload(row.items.select_related('item').all()),
        'can_post': row.status == 'draft',
        'can_edit': row.status == 'draft',
    }


def serialize_adjustment(row):
    return {
        'id': row.id,
        'number': row.adjustment_number,
        'adjustment_type': row.adjustment_type,
        'warehouse_id': row.warehouse_id,
        'warehouse_name': row.warehouse.name if row.warehouse_id else '',
        'adjustment_date': row.adjustment_date.isoformat() if row.adjustment_date else None,
        'status': row.status,
        'reason': row.reason or '',
        'notes': row.notes or '',
        'items': _lines_payload(row.items.select_related('item').all()),
        'can_post': row.status == 'draft',
        'can_edit': row.status == 'draft',
    }


def serialize_consumption(row):
    return {
        'id': row.id,
        'number': row.consumption_number,
        'kind': row.kind,
        'warehouse_id': row.warehouse_id,
        'warehouse_name': row.warehouse.name if row.warehouse_id else '',
        'revenue_center': row.revenue_center or '',
        'consumption_date': row.consumption_date.isoformat() if row.consumption_date else None,
        'status': row.status,
        'total_cost': _money(row.total_cost),
        'notes': row.notes or '',
        'items': _lines_payload(row.items.select_related('item').all()),
        'can_post': row.status == 'draft',
        'can_edit': row.status == 'draft',
    }


def serialize_payment(row):
    return {
        'id': row.id,
        'supplier_id': row.supplier_id,
        'supplier_name': row.supplier.name if row.supplier_id else '',
        'payment_date': row.payment_date.isoformat() if row.payment_date else None,
        'amount': _money(row.amount),
        'method': row.payment_method or 'cash',
        'reference': row.reference or '',
        'notes': row.notes or '',
        'created_by': _uname(row.created_by),
    }


def _supplier_due(supplier):
    purchases = Purchase.objects.filter(supplier=supplier, status=PurchaseStatus.RECEIVED, is_return=False)
    returns = Purchase.objects.filter(supplier=supplier, status=PurchaseStatus.RECEIVED, is_return=True)
    bought = purchases.aggregate(s=Sum('total_amount'))['s'] or Decimal('0')
    returned = returns.aggregate(s=Sum('total_amount'))['s'] or Decimal('0')
    paid = supplier.payments.aggregate(s=Sum('amount'))['s'] or Decimal('0')
    due = bought - returned - paid
    return due if due > 0 else Decimal('0')


def _parse_lines(tenant, lines, with_price=False):
    parsed = []
    for row in lines or []:
        item = _fk(InventoryItem, tenant, row.get('item_id'))
        qty = _dec(row.get('quantity'))
        if not item or qty <= 0:
            continue
        price = _dec(row.get('unit_price') or row.get('unit_cost') or item.cost_price)
        parsed.append((item, qty, price, qty * price))
    if not parsed:
        raise ValueError('Add at least one item with quantity')
    return parsed


def _set_req_lines(row, parsed):
    row.items.all().delete()
    for item, qty, _price, _total in parsed:
        RequisitionItem.objects.create(requisition=row, item=item, quantity=qty, unit=item.unit or 'Pcs')


def _set_pur_lines(row, parsed):
    row.items.all().delete()
    subtotal = Decimal('0')
    for item, qty, price, total in parsed:
        PurchaseItem.objects.create(purchase=row, item=item, quantity=qty, unit_price=price, total_price=total)
        subtotal += total
    row.subtotal = subtotal
    row.total_amount = subtotal + (row.tax_amount or 0) - (row.discount or 0)
    row.save()


def _set_trf_lines(row, parsed):
    row.items.all().delete()
    for item, qty, _p, _t in parsed:
        WarehouseTransferItem.objects.create(transfer=row, item=item, quantity=qty)


def _set_adj_lines(row, parsed):
    row.items.all().delete()
    for item, qty, _p, _t in parsed:
        StockAdjustmentItem.objects.create(adjustment=row, item=item, quantity=qty)


def _set_con_lines(row, parsed):
    row.items.all().delete()
    total = Decimal('0')
    for item, qty, price, line_total in parsed:
        cost = item.cost_price or price
        amt = qty * cost
        StockConsumptionItem.objects.create(
            consumption=row, item=item, quantity=qty, unit_cost=cost, total_cost=amt
        )
        total += amt
    row.total_cost = total
    row.save()


# --- posting ---

def post_purchase(row, user):
    if row.status == PurchaseStatus.RECEIVED:
        raise ValueError('Already posted')
    if row.status == PurchaseStatus.CANCELLED:
        raise ValueError('Cancelled')
    warehouse = row.warehouse
    if not warehouse:
        raise ValueError('Warehouse is required')
    day = row.purchase_date
    sign = Decimal('-1') if row.is_return else Decimal('1')
    ref = 'return' if row.is_return else 'purchase'
    for line in row.items.select_related('item'):
        _move(
            row.tenant, line.item, warehouse, sign * line.quantity, line.unit_price,
            ref, row.id, row.purchase_number, day, user,
        )
    row.status = PurchaseStatus.RECEIVED
    row.posted_at = timezone.now()
    row.save()
    try:
        from api.services.hotel_gl import post_inventory_purchase
        post_inventory_purchase(row, user=user)
    except Exception:
        # Stock receive must succeed even if GL seed is incomplete
        pass


def post_transfer(row, user):
    if row.status == 'posted':
        raise ValueError('Already posted')
    if row.from_warehouse_id == row.to_warehouse_id:
        raise ValueError('From and to warehouses must differ')
    day = row.transfer_date
    for line in row.items.select_related('item'):
        _move(row.tenant, line.item, row.from_warehouse, -line.quantity, line.item.cost_price, 'transfer_out', row.id, row.transfer_number, day, user)
        _move(row.tenant, line.item, row.to_warehouse, line.quantity, line.item.cost_price, 'transfer_in', row.id, row.transfer_number, day, user)
    row.status = 'posted'
    row.posted_at = timezone.now()
    row.save()


def post_adjustment(row, user):
    if row.status == 'posted':
        raise ValueError('Already posted')
    if not row.warehouse:
        raise ValueError('Warehouse is required')
    sign = Decimal('1') if row.adjustment_type == 'add' else Decimal('-1')
    ref = 'adj_add' if sign > 0 else 'adj_remove'
    for line in row.items.select_related('item'):
        _move(row.tenant, line.item, row.warehouse, sign * line.quantity, line.item.cost_price, ref, row.id, row.adjustment_number, row.adjustment_date, user, row.reason or '')
    row.status = 'posted'
    row.save()


def post_consumption(row, user):
    if row.status == 'posted':
        raise ValueError('Already posted')
    if not row.warehouse:
        raise ValueError('Warehouse is required')
    for line in row.items.select_related('item'):
        _move(row.tenant, line.item, row.warehouse, -line.quantity, line.unit_cost, 'consumption', row.id, row.consumption_number, row.consumption_date, user, row.revenue_center or '')
    row.status = 'posted'
    row.posted_at = timezone.now()
    row.save()


def post_requisition(row, user):
    if row.status == RequisitionStatus.FULFILLED:
        raise ValueError('Already fulfilled')
    if row.status != RequisitionStatus.APPROVED:
        raise ValueError('Approve the requisition before issuing stock')
    if not row.warehouse:
        raise ValueError('Warehouse is required')
    for line in row.items.select_related('item'):
        _move(row.tenant, line.item, row.warehouse, -line.quantity, line.item.cost_price, 'issue', row.id, row.requisition_number, row.requested_date, user, row.department or '')
    row.status = RequisitionStatus.FULFILLED
    row.save()


# --- config ---

SIMPLE = {
    'categories': InventoryCategory,
    'units': InventoryUnit,
    'warehouses': Warehouse,
}


def _list_config(kind, tenant):
    if kind in SIMPLE:
        return SIMPLE[kind].objects.filter(tenant=tenant).order_by('name')
    if kind == 'items':
        return InventoryItem.objects.select_related('category', 'warehouse').filter(tenant=tenant).order_by('name')
    if kind == 'suppliers':
        return Supplier.objects.filter(tenant=tenant).order_by('name')
    return None


def serialize_config(kind, row):
    if kind in SIMPLE or kind == 'suppliers':
        return serialize_named(row)
    if kind == 'items':
        return serialize_item(row)
    raise ValueError(kind)


def _save_config(kind, tenant, data, instance=None):
    name = (data.get('name') or '').strip()
    if kind in SIMPLE:
        if not name:
            raise ValueError('Name is required')
        kwargs = {'name': name, 'description': data.get('description') or '', 'is_active': _bool(data.get('is_active'), True)}
        if kind == 'warehouses':
            kwargs['location'] = data.get('location') or ''
        if instance:
            for k, v in kwargs.items():
                setattr(instance, k, v)
            instance.save()
            return instance
        return SIMPLE[kind].objects.create(tenant=tenant, **kwargs)
    if kind == 'suppliers':
        if not name:
            raise ValueError('Name is required')
        kwargs = {
            'name': name,
            'contact_person': data.get('contact_person') or '',
            'phone': data.get('phone') or '',
            'email': data.get('email') or '',
            'address': data.get('address') or '',
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            for k, v in kwargs.items():
                setattr(instance, k, v)
            instance.save()
            return instance
        return Supplier.objects.create(tenant=tenant, **kwargs)
    if kind == 'items':
        if not name:
            raise ValueError('Item name is required')
        code = (data.get('item_code') or '').strip()
        kwargs = {
            'name': name,
            'description': data.get('description') or '',
            'category': _fk(InventoryCategory, tenant, data.get('category_id')),
            'unit': data.get('unit') or 'Pcs',
            'min_stock_level': _dec(data.get('min_stock_level')),
            'cost_price': _dec(data.get('cost_price')) if data.get('cost_price') not in (None, '') else None,
            'selling_price': _dec(data.get('selling_price')) if data.get('selling_price') not in (None, '') else None,
            'warehouse': _fk(Warehouse, tenant, data.get('warehouse_id')),
            'supplier': _fk(Supplier, tenant, data.get('supplier_id')),
            'is_active': _bool(data.get('is_active'), True),
        }
        if instance:
            if code:
                kwargs['item_code'] = code
            for k, v in kwargs.items():
                setattr(instance, k, v)
            instance.save()
            return instance
        if not code:
            code = _num(InventoryItem, tenant, 'ITM')
        return InventoryItem.objects.create(tenant=tenant, item_code=code, **kwargs)
    raise ValueError(f'Unknown kind: {kind}')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    qs = _list_config(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    if request.method == 'POST':
        try:
            row = _save_config(kind, tenant, request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_config(kind, row), status=201)
    search = (request.query_params.get('search') or '').strip()
    if search:
        if kind == 'items':
            qs = qs.filter(Q(name__icontains=search) | Q(item_code__icontains=search))
        else:
            qs = qs.filter(name__icontains=search)
    items = [serialize_config(kind, row) for row in qs[:500]]
    extra = {}
    if kind == 'suppliers':
        extra['summary'] = {'due_total': round(sum(r['due_balance'] for r in items), 2)}
    return Response({'items': items, 'options': _options(tenant), **extra})


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    qs = _list_config(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    try:
        row = qs.get(id=pk)
    except qs.model.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        row.delete()
        return Response(status=204)
    if request.method in ('PATCH', 'PUT'):
        try:
            row = _save_config(kind, tenant, request.data or {}, instance=row)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_config(kind, row))
    return Response(serialize_config(kind, row))


# --- documents ---

def _want_post(data):
    return _bool(data.get('post'), False) or data.get('action') == 'post'


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def requisitions(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        try:
            parsed = _parse_lines(tenant, data.get('items') or [])
            row = Requisition.objects.create(
                tenant=tenant,
                requisition_number=data.get('number') or _num(Requisition, tenant, 'REQ'),
                requested_by=request.user,
                department=data.get('department') or '',
                warehouse=_fk(Warehouse, tenant, data.get('warehouse_id')),
                requested_date=_date(data.get('requested_date')) or date.today(),
                required_date=_date(data.get('required_date')),
                notes=data.get('notes') or '',
                status=RequisitionStatus.PENDING,
            )
            _set_req_lines(row, parsed)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_requisition(row), status=201)
    qs = Requisition.objects.select_related('requested_by', 'warehouse').filter(tenant=tenant).order_by('-id')[:200]
    return Response({'items': [serialize_requisition(r) for r in qs], 'options': _options(tenant)})


@api_view(['GET', 'PATCH', 'DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def requisition_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = Requisition.objects.get(pk=pk, tenant=tenant)
    except Requisition.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        if row.status != RequisitionStatus.PENDING:
            return Response({'detail': 'Only pending requisitions can be deleted'}, status=400)
        row.delete()
        return Response(status=204)
    if request.method == 'POST':
        action = (request.data or {}).get('action')
        try:
            if action == 'approve':
                row.status = RequisitionStatus.APPROVED
                row.approved_by = request.user
                row.approved_at = timezone.now()
                row.save()
            elif action == 'reject':
                row.status = RequisitionStatus.REJECTED
                row.save()
            elif action in ('fulfill', 'post', 'issue'):
                post_requisition(row, request.user)
            else:
                return Response({'detail': 'Use approve, reject, or fulfill'}, status=400)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_requisition(row))
    if request.method == 'PATCH':
        if row.status != RequisitionStatus.PENDING:
            return Response({'detail': 'Cannot edit after approval'}, status=400)
        data = request.data or {}
        try:
            if data.get('items') is not None:
                _set_req_lines(row, _parse_lines(tenant, data.get('items')))
            row.department = data.get('department', row.department)
            row.warehouse = _fk(Warehouse, tenant, data.get('warehouse_id')) or row.warehouse
            row.notes = data.get('notes', row.notes)
            if data.get('requested_date'):
                row.requested_date = _date(data.get('requested_date'))
            row.save()
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_requisition(row))
    return Response(serialize_requisition(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def purchases(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        supplier = _fk(Supplier, tenant, data.get('supplier_id'))
        warehouse = _fk(Warehouse, tenant, data.get('warehouse_id'))
        is_return = _bool(data.get('is_return'), False)
        try:
            if not supplier:
                raise ValueError('Supplier is required')
            if not warehouse:
                raise ValueError('Warehouse is required')
            parsed = _parse_lines(tenant, data.get('items') or [], with_price=True)
            prefix = 'RTN' if is_return else 'PUR'
            row = Purchase.objects.create(
                tenant=tenant,
                purchase_number=data.get('number') or _num(Purchase, tenant, prefix),
                supplier=supplier,
                warehouse=warehouse,
                is_return=is_return,
                purchase_date=_date(data.get('purchase_date')) or date.today(),
                tax_amount=_dec(data.get('tax_amount')),
                discount=_dec(data.get('discount')),
                total_amount=0,
                notes=data.get('notes') or '',
                status=PurchaseStatus.DRAFT,
                created_by=request.user,
            )
            _set_pur_lines(row, parsed)
            if _want_post(data):
                post_purchase(row, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_purchase(row), status=201)
    qs = Purchase.objects.select_related('supplier', 'warehouse').filter(tenant=tenant)
    if request.query_params.get('is_return') in ('1', 'true'):
        qs = qs.filter(is_return=True)
    qs = qs.order_by('-id')[:200]
    return Response({'items': [serialize_purchase(r) for r in qs], 'options': _options(tenant)})


@api_view(['GET', 'PATCH', 'DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def purchase_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = Purchase.objects.get(pk=pk, tenant=tenant)
    except Purchase.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        if row.status == PurchaseStatus.RECEIVED:
            return Response({'detail': 'Posted purchases cannot be deleted'}, status=400)
        row.delete()
        return Response(status=204)
    if request.method == 'POST':
        action = (request.data or {}).get('action')
        try:
            if action in ('post', 'receive'):
                post_purchase(row, request.user)
            elif action == 'cancel':
                if row.status == PurchaseStatus.RECEIVED:
                    raise ValueError('Posted purchases cannot be cancelled')
                row.status = PurchaseStatus.CANCELLED
                row.save()
            else:
                return Response({'detail': 'Use post or cancel'}, status=400)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_purchase(row))
    if request.method == 'PATCH':
        if row.status == PurchaseStatus.RECEIVED:
            return Response({'detail': 'Posted purchases cannot be edited'}, status=400)
        data = request.data or {}
        try:
            if data.get('items') is not None:
                _set_pur_lines(row, _parse_lines(tenant, data.get('items'), with_price=True))
            if data.get('supplier_id'):
                row.supplier = _fk(Supplier, tenant, data.get('supplier_id')) or row.supplier
            if data.get('warehouse_id'):
                row.warehouse = _fk(Warehouse, tenant, data.get('warehouse_id')) or row.warehouse
            row.notes = data.get('notes', row.notes)
            row.save()
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_purchase(row))
    return Response(serialize_purchase(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transfers(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        src = _fk(Warehouse, tenant, data.get('from_warehouse_id'))
        dst = _fk(Warehouse, tenant, data.get('to_warehouse_id'))
        try:
            if not src or not dst:
                raise ValueError('From and to warehouses are required')
            parsed = _parse_lines(tenant, data.get('items') or [])
            row = WarehouseTransfer.objects.create(
                tenant=tenant,
                transfer_number=_num(WarehouseTransfer, tenant, 'TRF'),
                from_warehouse=src,
                to_warehouse=dst,
                transfer_date=_date(data.get('transfer_date')) or date.today(),
                notes=data.get('notes') or '',
                status='draft',
                created_by=request.user,
            )
            _set_trf_lines(row, parsed)
            if _want_post(data):
                post_transfer(row, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_transfer(row), status=201)
    qs = WarehouseTransfer.objects.select_related('from_warehouse', 'to_warehouse').filter(tenant=tenant).order_by('-id')[:200]
    return Response({'items': [serialize_transfer(r) for r in qs], 'options': _options(tenant)})


@api_view(['GET', 'PATCH', 'DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def transfer_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = WarehouseTransfer.objects.get(pk=pk, tenant=tenant)
    except WarehouseTransfer.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        if row.status == 'posted':
            return Response({'detail': 'Posted transfers cannot be deleted'}, status=400)
        row.delete()
        return Response(status=204)
    if request.method == 'POST':
        try:
            if (request.data or {}).get('action') in ('post', 'receive'):
                post_transfer(row, request.user)
            else:
                return Response({'detail': 'Use post'}, status=400)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_transfer(row))
    return Response(serialize_transfer(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def adjustments(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        adj_type = (data.get('adjustment_type') or 'add').lower()
        if adj_type not in ('add', 'remove'):
            adj_type = 'add'
        try:
            warehouse = _fk(Warehouse, tenant, data.get('warehouse_id'))
            if not warehouse:
                raise ValueError('Warehouse is required')
            parsed = _parse_lines(tenant, data.get('items') or [])
            row = StockAdjustment.objects.create(
                tenant=tenant,
                adjustment_number=_num(StockAdjustment, tenant, 'ADJ'),
                adjustment_type=adj_type,
                warehouse=warehouse,
                adjustment_date=_date(data.get('adjustment_date')) or date.today(),
                reason=data.get('reason') or '',
                notes=data.get('notes') or '',
                status='draft',
                created_by=request.user,
            )
            _set_adj_lines(row, parsed)
            if _want_post(data):
                post_adjustment(row, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_adjustment(row), status=201)
    qs = StockAdjustment.objects.select_related('warehouse').filter(tenant=tenant)
    adj_type = request.query_params.get('type')
    if adj_type in ('add', 'remove'):
        qs = qs.filter(adjustment_type=adj_type)
    qs = qs.order_by('-id')[:200]
    return Response({'items': [serialize_adjustment(r) for r in qs], 'options': _options(tenant)})


@api_view(['GET', 'DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def adjustment_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = StockAdjustment.objects.get(pk=pk, tenant=tenant)
    except StockAdjustment.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        if row.status == 'posted':
            return Response({'detail': 'Posted adjustments cannot be deleted'}, status=400)
        row.delete()
        return Response(status=204)
    if request.method == 'POST':
        try:
            post_adjustment(row, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_adjustment(row))
    return Response(serialize_adjustment(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def consumptions(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        kind = (data.get('kind') or 'revenue_center').strip()
        if kind not in ('revenue_center', 'amenities'):
            kind = 'revenue_center'
        try:
            warehouse = _fk(Warehouse, tenant, data.get('warehouse_id'))
            if not warehouse:
                raise ValueError('Warehouse is required')
            parsed = _parse_lines(tenant, data.get('items') or [])
            row = StockConsumption.objects.create(
                tenant=tenant,
                consumption_number=_num(StockConsumption, tenant, 'CON'),
                kind=kind,
                warehouse=warehouse,
                revenue_center=data.get('revenue_center') or '',
                consumption_date=_date(data.get('consumption_date')) or date.today(),
                notes=data.get('notes') or '',
                status='draft',
                created_by=request.user,
            )
            _set_con_lines(row, parsed)
            if _want_post(data):
                post_consumption(row, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_consumption(row), status=201)
    qs = StockConsumption.objects.select_related('warehouse').filter(tenant=tenant)
    kind = request.query_params.get('kind')
    if kind:
        qs = qs.filter(kind=kind)
    qs = qs.order_by('-id')[:200]
    return Response({'items': [serialize_consumption(r) for r in qs], 'options': _options(tenant)})


@api_view(['GET', 'DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def consumption_detail(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = StockConsumption.objects.get(pk=pk, tenant=tenant)
    except StockConsumption.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    if request.method == 'DELETE':
        if row.status == 'posted':
            return Response({'detail': 'Posted consumptions cannot be deleted'}, status=400)
        row.delete()
        return Response(status=204)
    if request.method == 'POST':
        try:
            post_consumption(row, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_consumption(row))
    return Response(serialize_consumption(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def supplier_payments(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        supplier = _fk(Supplier, tenant, data.get('supplier_id'))
        amount = _dec(data.get('amount'))
        if not supplier:
            return Response({'detail': 'Supplier is required'}, status=400)
        if amount <= 0:
            return Response({'detail': 'Amount must be greater than zero'}, status=400)
        from django.db import transaction as db_transaction
        from api.services.hotel_gl import post_supplier_payment
        try:
            with db_transaction.atomic():
                row = SupplierPayment.objects.create(
                    tenant=tenant,
                    supplier=supplier,
                    payment_date=_date(data.get('payment_date')) or date.today(),
                    amount=amount,
                    payment_method=data.get('method') or data.get('payment_method') or 'cash',
                    reference=data.get('reference') or '',
                    notes=data.get('notes') or '',
                    created_by=request.user,
                )
                post_supplier_payment(row, user=request.user)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_payment(row), status=201)
    qs = SupplierPayment.objects.select_related('supplier').filter(
        Q(tenant=tenant) | Q(supplier__tenant=tenant)
    ).order_by('-payment_date', '-id')[:200]
    return Response({'items': [serialize_payment(r) for r in qs], 'options': _options(tenant)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_statement(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    supplier = _fk(Supplier, tenant, request.query_params.get('supplier_id'))
    options = _options(tenant)
    if not supplier:
        return Response({'columns': ['Date', 'Type', 'Reference', 'Debit', 'Credit', 'Balance'], 'rows': [], 'summary': {}, 'options': options})
    start = _date(request.query_params.get('from'))
    end = _date(request.query_params.get('to'))
    events = []
    for row in Purchase.objects.filter(supplier=supplier, status=PurchaseStatus.RECEIVED):
        day = row.purchase_date
        if start and day < start:
            continue
        if end and day > end:
            continue
        total = _money(row.total_amount)
        if row.is_return:
            events.append({'sort': day, 'date': day.isoformat(), 'type': 'Return', 'reference': row.purchase_number, 'debit': 0, 'credit': total})
        else:
            events.append({'sort': day, 'date': day.isoformat(), 'type': 'Purchase', 'reference': row.purchase_number, 'debit': total, 'credit': 0})
    for row in supplier.payments.all():
        day = row.payment_date
        if start and day < start:
            continue
        if end and day > end:
            continue
        events.append({'sort': day, 'date': day.isoformat(), 'type': 'Payment', 'reference': row.reference or str(row.id), 'debit': 0, 'credit': _money(row.amount)})
    events.sort(key=lambda e: e['sort'])
    balance = 0.0
    rows = []
    for event in events:
        balance += event['debit'] - event['credit']
        rows.append({**{k: event[k] for k in ('date', 'type', 'reference', 'debit', 'credit')}, 'balance': round(balance, 2)})
    return Response({
        'columns': ['Date', 'Type', 'Reference', 'Debit', 'Credit', 'Balance'],
        'rows': rows,
        'summary': {
            'supplier': supplier.name,
            'balance': round(balance, 2),
            'due': _money(_supplier_due(supplier)),
        },
        'options': options,
    })


# keep old /inventory/stock for current stock snapshot
def _current_stock_payload(tenant):
    _seed(tenant)
    rows = []
    stocks = InventoryStock.objects.select_related('item', 'warehouse', 'item__category').filter(tenant=tenant).order_by('item__name')
    if stocks.exists():
        for row in stocks:
            item = row.item
            rows.append({
                'item': item.name,
                'item_code': item.item_code,
                'category': item.category.name if item.category_id else '',
                'warehouse': row.warehouse.name,
                'unit': item.unit,
                'qty': _money(row.quantity),
                'cost': _money(item.cost_price),
                'value': _money((row.quantity or 0) * (item.cost_price or 0)),
                'min_stock': _money(item.min_stock_level),
                'status': 'low' if item.min_stock_level and row.quantity <= item.min_stock_level else 'ok',
            })
    else:
        for item in InventoryItem.objects.select_related('category', 'warehouse').filter(tenant=tenant).order_by('name'):
            rows.append({
                'item': item.name,
                'item_code': item.item_code,
                'category': item.category.name if item.category_id else '',
                'warehouse': item.warehouse.name if item.warehouse_id else '',
                'unit': item.unit,
                'qty': _money(item.current_stock),
                'cost': _money(item.cost_price),
                'value': _money((item.current_stock or 0) * (item.cost_price or 0)),
                'min_stock': _money(item.min_stock_level),
                'status': 'low' if item.min_stock_level and item.current_stock <= item.min_stock_level else 'ok',
            })
    return {
        'columns': ['Item', 'Code', 'Category', 'Warehouse', 'Unit', 'Qty', 'Cost', 'Value', 'Min', 'Status'],
        'rows': rows,
        'summary': {'value': round(sum(r['value'] for r in rows), 2), 'lines': len(rows)},
        'items': rows,
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    return Response(_current_stock_payload(tenant))


def _period(request):
    today = date.today()
    start = _date(request.query_params.get('from')) or today.replace(day=1)
    end = _date(request.query_params.get('to')) or today
    if end < start:
        start, end = end, start
    return start, end


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    start, end = _period(request)

    if kind == 'current-stock':
        return Response(_current_stock_payload(tenant))

    if kind == 'stock-register':
        item = _fk(InventoryItem, tenant, request.query_params.get('item_id'))
        warehouse = _fk(Warehouse, tenant, request.query_params.get('warehouse_id'))
        qs = InventoryMovement.objects.select_related('item', 'warehouse').filter(
            tenant=tenant, movement_date__gte=start, movement_date__lte=end
        )
        if item:
            qs = qs.filter(item=item)
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        qs = qs.order_by('movement_date', 'id')
        balance = 0.0
        rows = []
        for row in qs:
            qty = _money(row.quantity)
            balance += qty
            rows.append({
                'date': row.movement_date.isoformat(),
                'item': row.item.name,
                'warehouse': row.warehouse.name,
                'type': row.ref_type,
                'reference': row.ref_number or '',
                'in': qty if qty > 0 else 0,
                'out': -qty if qty < 0 else 0,
                'balance': round(balance, 2),
            })
        return Response({
            'columns': ['Date', 'Item', 'Warehouse', 'Type', 'Reference', 'In', 'Out', 'Balance'],
            'rows': rows,
            'summary': {'movements': len(rows)},
            'options': _options(tenant),
        })

    if kind == 'inventory':
        grouped = defaultdict(lambda: {'opening': 0.0, 'in': 0.0, 'out': 0.0})
        prior = InventoryMovement.objects.filter(tenant=tenant, movement_date__lt=start)
        for row in prior:
            grouped[(row.item_id, row.warehouse_id)]['opening'] += _money(row.quantity)
        period = InventoryMovement.objects.select_related('item', 'warehouse').filter(
            tenant=tenant, movement_date__gte=start, movement_date__lte=end
        )
        names = {}
        for row in period:
            key = (row.item_id, row.warehouse_id)
            names[key] = (row.item.name, row.warehouse.name, row.item.unit, row.item.cost_price)
            qty = _money(row.quantity)
            if qty >= 0:
                grouped[key]['in'] += qty
            else:
                grouped[key]['out'] += -qty
        rows = []
        for key, vals in grouped.items():
            name = names.get(key)
            if not name:
                item = InventoryItem.objects.filter(id=key[0]).first()
                wh = Warehouse.objects.filter(id=key[1]).first()
                if not item or not wh:
                    continue
                name = (item.name, wh.name, item.unit, item.cost_price)
            closing = vals['opening'] + vals['in'] - vals['out']
            rows.append({
                'item': name[0],
                'warehouse': name[1],
                'unit': name[2],
                'opening': round(vals['opening'], 2),
                'in': round(vals['in'], 2),
                'out': round(vals['out'], 2),
                'closing': round(closing, 2),
                'value': round(closing * _money(name[3]), 2),
            })
        rows.sort(key=lambda r: (r['item'], r['warehouse']))
        return Response({
            'columns': ['Item', 'Warehouse', 'Unit', 'Opening', 'In', 'Out', 'Closing', 'Value'],
            'rows': rows,
            'summary': {'value': round(sum(r['value'] for r in rows), 2)},
        })

    if kind == 'purchase':
        rows = []
        qs = Purchase.objects.select_related('supplier', 'warehouse').filter(
            tenant=tenant, status=PurchaseStatus.RECEIVED,
            purchase_date__gte=start, purchase_date__lte=end,
        ).order_by('purchase_date')
        for row in qs:
            rows.append({
                'date': row.purchase_date.isoformat(),
                'number': row.purchase_number,
                'type': 'Return' if row.is_return else 'Purchase',
                'supplier': row.supplier.name if row.supplier_id else '',
                'warehouse': row.warehouse.name if row.warehouse_id else '',
                'amount': _money(row.total_amount) * (-1 if row.is_return else 1),
            })
        return Response({
            'columns': ['Date', 'Number', 'Type', 'Supplier', 'Warehouse', 'Amount'],
            'rows': rows,
            'summary': {'amount': round(sum(r['amount'] for r in rows), 2)},
        })

    if kind == 'warehouse-transfer':
        rows = []
        qs = WarehouseTransfer.objects.select_related('from_warehouse', 'to_warehouse').prefetch_related('items__item').filter(
            tenant=tenant, status='posted',
            transfer_date__gte=start, transfer_date__lte=end,
        ).order_by('transfer_date')
        for row in qs:
            for line in row.items.all():
                rows.append({
                    'date': row.transfer_date.isoformat(),
                    'number': row.transfer_number,
                    'from': row.from_warehouse.name,
                    'to': row.to_warehouse.name,
                    'item': line.item.name,
                    'qty': _money(line.quantity),
                })
        return Response({
            'columns': ['Date', 'Number', 'From', 'To', 'Item', 'Qty'],
            'rows': rows,
            'summary': {'lines': len(rows)},
        })

    if kind == 'item-wise-purchase':
        grouped = defaultdict(lambda: {'qty': 0.0, 'amount': 0.0})
        lines = PurchaseItem.objects.select_related('item', 'purchase').filter(
            purchase__tenant=tenant,
            purchase__status=PurchaseStatus.RECEIVED,
            purchase__purchase_date__gte=start,
            purchase__purchase_date__lte=end,
        )
        for line in lines:
            sign = -1 if line.purchase.is_return else 1
            grouped[line.item.name]['qty'] += sign * _money(line.quantity)
            grouped[line.item.name]['amount'] += sign * _money(line.total_price)
        rows = [{'item': name, 'qty': round(v['qty'], 2), 'amount': round(v['amount'], 2)} for name, v in sorted(grouped.items())]
        return Response({
            'columns': ['Item', 'Qty', 'Amount'],
            'rows': rows,
            'summary': {'amount': round(sum(r['amount'] for r in rows), 2)},
        })

    if kind == 'cost-of-consumption':
        rows = []
        qs = StockConsumption.objects.select_related('warehouse').filter(
            tenant=tenant, status='posted',
            consumption_date__gte=start, consumption_date__lte=end,
        ).order_by('consumption_date')
        for row in qs:
            rows.append({
                'date': row.consumption_date.isoformat(),
                'number': row.consumption_number,
                'kind': 'Amenities' if row.kind == 'amenities' else 'Revenue center',
                'center': row.revenue_center or '',
                'warehouse': row.warehouse.name if row.warehouse_id else '',
                'cost': _money(row.total_cost),
            })
        return Response({
            'columns': ['Date', 'Number', 'Kind', 'Center / amenity', 'Warehouse', 'Cost'],
            'rows': rows,
            'summary': {'cost': round(sum(r['cost'] for r in rows), 2)},
        })

    return Response({'detail': f'Unknown report: {kind}'}, status=400)
