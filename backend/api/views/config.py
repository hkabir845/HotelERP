"""Generic named-record CRUD for GYOROOM config screens."""
from datetime import date

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    Asset,
    AssetCategory,
    BedInfo,
    BoardType,
    BookingAgent,
    CancellationRule,
    ChartOfAccount,
    Company,
    ComplimentaryOption,
    ExtraChargeGroup,
    ExtraChargeItem,
    GuestSource,
    InventoryCategory,
    InventoryItem,
    JournalEntry,
    Package,
    Purchase,
    RatePlan,
    Requisition,
    Room,
    RoomFacility,
    RoomGroup,
    RoomType,
    RoomViewType,
    Supplier,
    Warehouse,
)
from api.views import deny_if_no_tenant

KIND_MODEL = {
    'packages': Package,
    'room-view-types': RoomViewType,
    'bed-info': BedInfo,
    'room-facilities': RoomFacility,
    'room-groups': RoomGroup,
    'room-types': RoomType,
    'rooms': Room,
    'extra-charge-items': ExtraChargeItem,
    'extra-charge-groups': ExtraChargeGroup,
    'booking-agents': BookingAgent,
    'companies': Company,
    'rate-plans': RatePlan,
    'cancellation-rules': CancellationRule,
    'board-types': BoardType,
    'complimentary-options': ComplimentaryOption,
    'guest-sources': GuestSource,
    'inventory-items': InventoryItem,
    'inventory-categories': InventoryCategory,
    'inventory-units': InventoryCategory,
    'inventory-warehouses': Warehouse,
    'inventory-suppliers': Supplier,
    'accounts': ChartOfAccount,
    'account-groups': ChartOfAccount,
    'chart-of-accounts': ChartOfAccount,
    'asset-types': AssetCategory,
    'asset-categories': AssetCategory,
    'assets': Asset,
    'asset-vendors': AssetCategory,
    'vouchers': JournalEntry,
    'cash-payment': JournalEntry,
    'bank-payment': JournalEntry,
    'cash-receipt': JournalEntry,
    'bank-receipt': JournalEntry,
    'contra': JournalEntry,
    'journal': JournalEntry,
    'requisitions': Requisition,
    'purchases': Purchase,
}

VOUCHER_PREFIX = {
    'cash-payment': 'CPV',
    'bank-payment': 'BPV',
    'cash-receipt': 'CRV',
    'bank-receipt': 'BRV',
    'contra': 'CV',
    'journal': 'JV',
    'vouchers': 'V',
}


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _serialize(obj):
    name = (
        getattr(obj, 'name', None)
        or getattr(obj, 'account_name', None)
        or getattr(obj, 'entry_number', None)
        or getattr(obj, 'room_number', None)
        or getattr(obj, 'asset_name', None)
        or str(obj.pk)
    )
    code = (
        getattr(obj, 'account_code', None)
        or getattr(obj, 'entry_number', None)
        or getattr(obj, 'reference', None)
        or getattr(obj, 'item_code', None)
        or getattr(obj, 'asset_code', None)
        or getattr(obj, 'entry_number', None)
        or (str(obj.floor) if getattr(obj, 'floor', None) is not None else None)
        or getattr(obj, 'contact_person', None)
        or getattr(obj, 'sku', None)
        or ''
    )
    amount = (
        getattr(obj, 'price', None)
        or getattr(obj, 'amount', None)
        or getattr(obj, 'base_rate', None)
        or getattr(obj, 'rack_rate', None)
        or getattr(obj, 'additional_charge', None)
        or getattr(obj, 'unit_cost', None)
        or 0
    )
    notes = (
        getattr(obj, 'description', None)
        or getattr(obj, 'notes', None)
        or getattr(obj, 'address', None)
        or ''
    )
    if getattr(obj, 'is_active', None) is False:
        row_status = 'inactive'
    else:
        row_status = getattr(obj, 'status', None) or 'active'
    return {
        'id': obj.id,
        'name': name,
        'code': code or '',
        'amount': float(amount or 0),
        'status': row_status,
        'notes': notes or '',
    }


def _create(model, tenant, data, user=None):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('name is required')
    amount = data.get('amount') or 0
    notes = data.get('notes') or ''
    code = data.get('code') or ''
    kwargs = {'tenant': tenant}

    if model is Room:
        room_type = RoomType.objects.filter(tenant=tenant).first()
        if not room_type:
            room_type = RoomType.objects.create(
                tenant=tenant, name='Standard', base_rate=amount or 0
            )
        kwargs.update(
            room_number=name,
            room_type=room_type,
            floor=int(code) if str(code).isdigit() else None,
            rack_rate=amount or None,
            notes=notes,
        )
        return model.objects.create(**kwargs)
    if model is RoomType:
        kwargs.update(name=name, description=notes, base_rate=amount or 0)
        return model.objects.create(**kwargs)
    if model is Package:
        kwargs.update(name=name, description=notes, price=amount or 0)
        return model.objects.create(**kwargs)
    if model is ExtraChargeItem:
        kwargs.update(name=name, description=notes, amount=amount or 0)
        return model.objects.create(**kwargs)
    if model is BoardType:
        kwargs.update(name=name, description=notes, additional_charge=amount or 0)
        return model.objects.create(**kwargs)
    if model is ChartOfAccount:
        kwargs.update(
            account_name=name,
            account_code=code or f'A-{tenant.id}-{ChartOfAccount.objects.filter(tenant=tenant).count() + 1:04d}',
            account_type=data.get('account_type') or 'expense',
        )
        return model.objects.create(**kwargs)
    if model is InventoryItem:
        n = InventoryItem.objects.filter(tenant=tenant).count() + 1
        return InventoryItem.objects.create(
            tenant=tenant,
            name=name,
            item_code=code or f'ITM-{tenant.id}-{n:05d}',
            description=notes or None,
            unit='pcs',
            cost_price=amount or 0,
        )
    if model is Asset:
        category = AssetCategory.objects.filter(tenant=tenant).first()
        if not category:
            category = AssetCategory.objects.create(tenant=tenant, name='General')
        n = Asset.objects.filter(tenant=tenant).count() + 1
        return Asset.objects.create(
            tenant=tenant,
            name=name,
            asset_code=code or f'AST-{tenant.id}-{n:05d}',
            category=category,
            purchase_price=amount or 0,
            notes=notes or None,
        )
    if model is JournalEntry:
        n = JournalEntry.objects.filter(tenant=tenant).count() + 1
        amt = amount or 0
        kind = data.get('kind') or 'vouchers'
        prefix = VOUCHER_PREFIX.get(kind, 'V')
        return JournalEntry.objects.create(
            tenant=tenant,
            entry_number=code or f'{prefix}-{tenant.id}-{n:05d}',
            entry_date=date.today(),
            reference=kind,
            description=notes or name,
            total_debit=amt,
            total_credit=amt,
        )
    if model is Requisition:
        n = Requisition.objects.filter(tenant=tenant).count() + 1
        return Requisition.objects.create(
            tenant=tenant,
            requisition_number=code or f'REQ-{tenant.id}-{n:05d}',
            requested_by=user,
            department=notes or name,
            requested_date=date.today(),
            notes=notes or None,
        )
    if model is Purchase:
        supplier = Supplier.objects.filter(tenant=tenant).first()
        if not supplier:
            supplier = Supplier.objects.create(tenant=tenant, name='General supplier')
        n = Purchase.objects.filter(tenant=tenant).count() + 1
        return Purchase.objects.create(
            tenant=tenant,
            purchase_number=code or f'PUR-{tenant.id}-{n:05d}',
            supplier=supplier,
            purchase_date=date.today(),
            total_amount=amount or 0,
            notes=notes or name,
        )
    if model is Warehouse:
        kwargs.update(name=name, location=notes or code or None)
        return model.objects.create(**kwargs)
    if model is Supplier:
        kwargs.update(name=name, contact_person=code or None, phone=None, address=notes or None)
        try:
            return model.objects.create(**kwargs)
        except Exception:
            return model.objects.create(tenant=tenant, name=name)

    field_names = {f.name for f in model._meta.fields}
    if 'name' in field_names:
        kwargs['name'] = name
    if 'description' in field_names:
        kwargs['description'] = notes
    if 'notes' in field_names and 'description' not in field_names:
        kwargs['notes'] = notes
    if 'email' in field_names and '@' in (code or ''):
        kwargs['email'] = code
    elif 'contact_person' in field_names and code:
        kwargs['contact_person'] = code
    if 'phone' in field_names and code and '@' not in code:
        kwargs['phone'] = code
    if 'amount' in field_names:
        kwargs['amount'] = amount or 0
    if 'price' in field_names:
        kwargs['price'] = amount or 0
    return model.objects.create(**kwargs)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def config_records(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    kind = (request.query_params.get('kind') or request.data.get('kind') or '').strip()
    model = KIND_MODEL.get(kind)
    if not model:
        return Response({'detail': f'Unknown config kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        try:
            row = _create(model, tenant, request.data or {}, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_serialize(row), status=status.HTTP_201_CREATED)
    qs = model.objects.filter(tenant=tenant)
    if kind in VOUCHER_PREFIX and kind != 'vouchers':
        qs = qs.filter(reference=kind)
    qs = qs.order_by('-id')[:300]
    return Response({'items': [_serialize(r) for r in qs]})
