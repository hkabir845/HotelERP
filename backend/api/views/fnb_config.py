"""F&B masters, POS customers, expenses, and outlet reports."""
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    FnbCategory,
    FnbExpense,
    FnbExpenseCategory,
    FnbExpenseHead,
    FnbSubCategory,
    FnbToken,
    FnbUnit,
    Menu,
    MenuItem,
    Order,
    OrderItem,
    OrderStatus,
    PosCustomer,
    PosDueReceive,
    Reservation,
    ReservationStatus,
    RevenueCenter,
    ServeBy,
    TakeAwayAgent,
)
from api.views import deny_if_no_tenant

SIMPLE_KINDS = {
    'revenue-centers': RevenueCenter,
    'categories': FnbCategory,
    'units': FnbUnit,
    'tokens': FnbToken,
    'serve-by': ServeBy,
    'take-away-agents': TakeAwayAgent,
    'expense-categories': FnbExpenseCategory,
}


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


def _uname(user):
    if not user:
        return 'Unknown'
    full = f'{user.first_name or ""} {user.last_name or ""}'.strip()
    return full or user.username or user.email or 'Unknown'


def _money(value):
    return float(value or 0)


def _order_due(order):
    due = (order.total_amount or Decimal('0')) - (order.paid_amount or Decimal('0'))
    return due if due > 0 else Decimal('0')


def _customer_due(customer):
    orders = Order.objects.filter(tenant=customer.tenant, pos_customer=customer).exclude(
        status=OrderStatus.CANCELLED
    )
    outstanding = Decimal('0')
    for order in orders:
        outstanding += _order_due(order)
    received = customer.due_receives.aggregate(s=Sum('amount'))['s'] or Decimal('0')
    due = outstanding - received
    return due if due > 0 else Decimal('0')


def _ensure_menu(tenant):
    menu = Menu.objects.filter(tenant=tenant).first()
    if not menu:
        menu = Menu.objects.create(tenant=tenant, name='Main menu')
    return menu


def _seed(tenant):
    if not RevenueCenter.objects.filter(tenant=tenant).exists():
        for name in ('Restaurant', 'Room Service', 'Banquet'):
            RevenueCenter.objects.create(tenant=tenant, name=name)
    if not FnbCategory.objects.filter(tenant=tenant).exists():
        food = FnbCategory.objects.create(tenant=tenant, name='Food')
        beverage = FnbCategory.objects.create(tenant=tenant, name='Beverage')
        FnbSubCategory.objects.create(tenant=tenant, name='Main Course', category=food)
        FnbSubCategory.objects.create(tenant=tenant, name='Appetizer', category=food)
        FnbSubCategory.objects.create(tenant=tenant, name='Soft Drink', category=beverage)
        FnbSubCategory.objects.create(tenant=tenant, name='Hot Beverage', category=beverage)
    if not FnbUnit.objects.filter(tenant=tenant).exists():
        for name in ('Pcs', 'Plate', 'Glass', 'Bottle'):
            FnbUnit.objects.create(tenant=tenant, name=name)
    if not FnbToken.objects.filter(tenant=tenant).exists():
        for name in ('Kitchen', 'Bar'):
            FnbToken.objects.create(tenant=tenant, name=name)
    if not FnbExpenseCategory.objects.filter(tenant=tenant).exists():
        kitchen = FnbExpenseCategory.objects.create(tenant=tenant, name='Kitchen')
        FnbExpenseHead.objects.create(tenant=tenant, name='Gas & Fuel', category=kitchen)
        FnbExpenseHead.objects.create(tenant=tenant, name='Packaging', category=kitchen)


def _options(tenant):
    return {
        'revenue_centers': _opt(RevenueCenter.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'categories': _opt(FnbCategory.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'sub_categories': _opt(FnbSubCategory.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'units': _opt(FnbUnit.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'tokens': _opt(FnbToken.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'expense_categories': _opt(
            FnbExpenseCategory.objects.filter(tenant=tenant, is_active=True).order_by('name')
        ),
        'expense_heads': _opt(FnbExpenseHead.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'pos_customers': _opt(PosCustomer.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'payment_methods': [
            {'id': 'cash', 'name': 'Cash'},
            {'id': 'card', 'name': 'Card'},
            {'id': 'bank', 'name': 'Bank'},
            {'id': 'mobile', 'name': 'Mobile'},
        ],
    }


def serialize_named(row):
    data = {
        'id': row.id,
        'name': row.name,
        'description': getattr(row, 'description', None) or '',
        'is_active': getattr(row, 'is_active', True),
    }
    if hasattr(row, 'phone'):
        data['phone'] = row.phone or ''
    if hasattr(row, 'commission_rate'):
        data['commission_rate'] = float(row.commission_rate) if row.commission_rate is not None else None
    if hasattr(row, 'category_id'):
        data['category_id'] = row.category_id
        data['category_name'] = row.category.name if row.category_id else ''
    return data


def serialize_item(row):
    return {
        'id': row.id,
        'name': row.name,
        'description': row.description or '',
        'category': row.category or '',
        'subcategory': row.subcategory or '',
        'price': _money(row.price),
        'cost': _money(row.cost) if row.cost is not None else None,
        'unit': row.unit or '',
        'token': row.token or '',
        'revenue_center': row.revenue_center or '',
        'is_available': row.is_available,
        'is_active': row.is_available,
    }


def serialize_customer(row):
    due = _customer_due(row)
    return {
        'id': row.id,
        'name': row.name,
        'phone': row.phone or '',
        'email': row.email or '',
        'address': row.address or '',
        'credit_limit': _money(row.credit_limit),
        'due_balance': _money(due),
        'is_active': row.is_active,
    }


def serialize_due(row):
    return {
        'id': row.id,
        'customer_id': row.customer_id,
        'customer_name': row.customer.name if row.customer_id else '',
        'receive_date': row.receive_date.isoformat() if row.receive_date else None,
        'amount': _money(row.amount),
        'method': row.method or 'cash',
        'notes': row.notes or '',
        'created_at': row.created_at.isoformat() if row.created_at else None,
        'created_by': _uname(row.created_by) if row.created_by_id else '',
    }


def serialize_expense(row):
    return {
        'id': row.id,
        'head_id': row.head_id,
        'head_name': row.head.name if row.head_id else '',
        'category_name': row.head.category.name if row.head_id and row.head.category_id else '',
        'expense_date': row.expense_date.isoformat() if row.expense_date else None,
        'amount': _money(row.amount),
        'revenue_center': row.revenue_center or '',
        'notes': row.notes or '',
        'created_by': _uname(row.created_by) if row.created_by_id else '',
    }


def _list_qs(kind, tenant):
    if kind in SIMPLE_KINDS:
        return SIMPLE_KINDS[kind].objects.filter(tenant=tenant).order_by('name')
    if kind == 'sub-categories':
        return FnbSubCategory.objects.select_related('category').filter(tenant=tenant).order_by('name')
    if kind == 'items':
        return MenuItem.objects.filter(tenant=tenant).order_by('category', 'name')
    if kind == 'pos-customers':
        return PosCustomer.objects.filter(tenant=tenant).order_by('name')
    if kind == 'due-receives':
        return (
            PosDueReceive.objects.select_related('customer', 'created_by')
            .filter(tenant=tenant)
            .order_by('-receive_date', '-id')
        )
    if kind == 'expense-heads':
        return FnbExpenseHead.objects.select_related('category').filter(tenant=tenant).order_by('name')
    if kind == 'expenses':
        return (
            FnbExpense.objects.select_related('head', 'head__category', 'created_by')
            .filter(tenant=tenant)
            .order_by('-expense_date', '-id')
        )
    return None


def serialize_kind(kind, row):
    if kind in SIMPLE_KINDS or kind in ('sub-categories', 'expense-heads'):
        return serialize_named(row)
    if kind == 'items':
        return serialize_item(row)
    if kind == 'pos-customers':
        return serialize_customer(row)
    if kind == 'due-receives':
        return serialize_due(row)
    if kind == 'expenses':
        return serialize_expense(row)
    raise ValueError(f'Unknown kind: {kind}')


def _named_kwargs(data):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Name is required')
    return {
        'name': name,
        'description': data.get('description') or '',
        'is_active': _bool(data.get('is_active'), True),
    }


def _save(model, tenant, kwargs, instance=None):
    if instance:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    return model.objects.create(tenant=tenant, **kwargs)


def _create_or_update(kind, tenant, data, instance=None, user=None):
    if kind in SIMPLE_KINDS:
        kwargs = _named_kwargs(data)
        if kind == 'serve-by':
            kwargs['phone'] = data.get('phone') or ''
        if kind == 'take-away-agents':
            kwargs['phone'] = data.get('phone') or ''
            kwargs['commission_rate'] = (
                _dec(data.get('commission_rate')) if data.get('commission_rate') not in (None, '') else None
            )
        return _save(SIMPLE_KINDS[kind], tenant, kwargs, instance)

    if kind == 'sub-categories':
        kwargs = _named_kwargs(data)
        kwargs['category'] = _fk(FnbCategory, tenant, data.get('category_id'))
        if instance and not kwargs['category']:
            kwargs['category'] = instance.category
        return _save(FnbSubCategory, tenant, kwargs, instance)

    if kind == 'expense-heads':
        kwargs = _named_kwargs(data)
        kwargs['category'] = _fk(FnbExpenseCategory, tenant, data.get('category_id'))
        if instance and not kwargs['category']:
            kwargs['category'] = instance.category
        return _save(FnbExpenseHead, tenant, kwargs, instance)

    if kind == 'items':
        kwargs = {
            'name': (data.get('name') or '').strip(),
            'description': data.get('description') or '',
            'category': data.get('category') or '',
            'subcategory': data.get('subcategory') or '',
            'price': _dec(data.get('price') or data.get('amount')),
            'cost': _dec(data.get('cost')) if data.get('cost') not in (None, '') else None,
            'unit': data.get('unit') or '',
            'token': data.get('token') or '',
            'revenue_center': data.get('revenue_center') or '',
            'is_available': _bool(data.get('is_available', data.get('is_active')), True),
        }
        if not kwargs['name']:
            raise ValueError('Item name is required')
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        return MenuItem.objects.create(tenant=tenant, menu=_ensure_menu(tenant), **kwargs)

    if kind == 'pos-customers':
        name = (data.get('name') or '').strip()
        if not name:
            raise ValueError('Customer name is required')
        kwargs = {
            'name': name,
            'phone': data.get('phone') or '',
            'email': data.get('email') or '',
            'address': data.get('address') or '',
            'credit_limit': _dec(data.get('credit_limit')),
            'is_active': _bool(data.get('is_active'), True),
        }
        return _save(PosCustomer, tenant, kwargs, instance)

    if kind == 'due-receives':
        customer = _fk(PosCustomer, tenant, data.get('customer_id'))
        if instance and not customer:
            customer = instance.customer
        if not customer:
            raise ValueError('Customer is required')
        amount = _dec(data.get('amount'))
        if amount <= 0:
            raise ValueError('Amount must be greater than zero')
        receive_date = _date(data.get('receive_date')) or date.today()
        kwargs = {
            'customer': customer,
            'receive_date': receive_date,
            'amount': amount,
            'method': data.get('method') or 'cash',
            'notes': data.get('notes') or '',
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        kwargs['created_by'] = user
        return PosDueReceive.objects.create(tenant=tenant, **kwargs)

    if kind == 'expenses':
        head = _fk(FnbExpenseHead, tenant, data.get('head_id'))
        if instance and not head:
            head = instance.head
        if not head:
            raise ValueError('Expense head is required')
        amount = _dec(data.get('amount'))
        if amount <= 0:
            raise ValueError('Amount must be greater than zero')
        kwargs = {
            'head': head,
            'expense_date': _date(data.get('expense_date')) or date.today(),
            'amount': amount,
            'revenue_center': data.get('revenue_center') or '',
            'notes': data.get('notes') or '',
        }
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        kwargs['created_by'] = user
        return FnbExpense.objects.create(tenant=tenant, **kwargs)

    raise ValueError(f'Unknown kind: {kind}')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    _seed(tenant)
    qs = _list_qs(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        try:
            row = _create_or_update(kind, tenant, request.data or {}, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_kind(kind, row), status=status.HTTP_201_CREATED)
    search = (request.query_params.get('search') or '').strip()
    if search:
        if kind == 'items':
            qs = qs.filter(Q(name__icontains=search) | Q(category__icontains=search) | Q(subcategory__icontains=search))
        elif kind == 'due-receives':
            qs = qs.filter(Q(customer__name__icontains=search) | Q(notes__icontains=search))
        elif kind == 'expenses':
            qs = qs.filter(Q(head__name__icontains=search) | Q(notes__icontains=search))
        elif hasattr(qs.model, 'name'):
            qs = qs.filter(Q(name__icontains=search))
    items = [serialize_kind(kind, row) for row in qs[:500]]
    extra = {}
    if kind == 'pos-customers':
        extra['summary'] = {
            'customers': len(items),
            'due_total': round(sum(row['due_balance'] for row in items), 2),
        }
    return Response({'items': items, 'options': _options(tenant), **extra})


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    qs = _list_qs(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        row = qs.get(id=pk)
    except qs.model.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        if kind == 'items' and row.order_items.exists():
            return Response(
                {'detail': 'This item has sales. Mark it unavailable instead of deleting.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if kind == 'pos-customers' and row.orders.exists():
            return Response(
                {'detail': 'This customer has orders. Deactivate instead of deleting.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method in ('PATCH', 'PUT'):
        try:
            row = _create_or_update(kind, tenant, request.data or {}, instance=row, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_kind(kind, row))
    return Response(serialize_kind(kind, row))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pos_statement(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    customer = _fk(PosCustomer, tenant, request.query_params.get('customer_id'))
    options = _options(tenant)
    if not customer:
        return Response({
            'columns': ['Date', 'Type', 'Reference', 'Debit', 'Credit', 'Balance'],
            'rows': [],
            'summary': {},
            'options': options,
        })
    start = _date(request.query_params.get('from'))
    end = _date(request.query_params.get('to'))
    orders = list(
        Order.objects.filter(tenant=tenant, pos_customer=customer)
        .exclude(status=OrderStatus.CANCELLED)
        .order_by('created_at')
    )
    receives = list(customer.due_receives.order_by('receive_date', 'id'))
    events = []
    for order in orders:
        day = (order.created_at or datetime.now()).date()
        if start and day < start:
            continue
        if end and day > end:
            continue
        events.append({
            'sort': order.created_at or datetime.now(),
            'date': day.isoformat(),
            'type': 'Sale',
            'reference': order.order_number,
            'debit': _money(order.total_amount),
            'credit': _money(order.paid_amount),
        })
    for rec in receives:
        if start and rec.receive_date < start:
            continue
        if end and rec.receive_date > end:
            continue
        events.append({
            'sort': datetime.combine(rec.receive_date, datetime.min.time()),
            'date': rec.receive_date.isoformat(),
            'type': 'Due receive',
            'reference': rec.method or 'cash',
            'debit': 0,
            'credit': _money(rec.amount),
        })
    events.sort(key=lambda row: row['sort'])
    balance = 0.0
    rows = []
    for event in events:
        balance += event['debit'] - event['credit']
        rows.append({
            'date': event['date'],
            'type': event['type'],
            'reference': event['reference'],
            'debit': event['debit'],
            'credit': event['credit'],
            'balance': round(balance, 2),
        })
    sales_total = sum(event['debit'] for event in events if event['type'] == 'Sale')
    paid_total = sum(event['credit'] for event in events if event['type'] == 'Sale')
    received_total = sum(event['credit'] for event in events if event['type'] == 'Due receive')
    return Response({
        'columns': ['Date', 'Type', 'Reference', 'Debit', 'Credit', 'Balance'],
        'rows': rows,
        'summary': {
            'customer': customer.name,
            'sales': round(sales_total, 2),
            'paid_at_sale': round(paid_total, 2),
            'due_received': round(received_total, 2),
            'balance': round(balance, 2),
            'credit_limit': _money(customer.credit_limit),
        },
        'options': options,
    })


def _period(request):
    today = date.today()
    start = _date(request.query_params.get('from')) or today.replace(day=1)
    end = _date(request.query_params.get('to')) or today
    if end < start:
        start, end = end, start
    return start, end


def _orders_in(tenant, start, end, include_cancelled=False):
    qs = Order.objects.filter(tenant=tenant, created_at__date__gte=start, created_at__date__lte=end)
    if not include_cancelled:
        qs = qs.exclude(status=OrderStatus.CANCELLED)
    return qs.select_related('room', 'table', 'pos_customer', 'created_by').prefetch_related('items')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fnb_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    start, end = _period(request)

    if kind == 'sales-sheet':
        grouped = defaultdict(lambda: {'orders': 0, 'subtotal': 0.0, 'tax': 0.0, 'discount': 0.0, 'total': 0.0, 'paid': 0.0})
        for order in _orders_in(tenant, start, end):
            center = order.revenue_center or (
                'Room Service' if order.order_type == 'room_service' else 'Restaurant'
            )
            row = grouped[center]
            row['orders'] += 1
            row['subtotal'] += _money(order.subtotal)
            row['tax'] += _money(order.tax_amount)
            row['discount'] += _money(order.discount)
            row['total'] += _money(order.total_amount)
            row['paid'] += _money(order.paid_amount)
        rows = [
            {'revenue_center': name, **vals, 'due': round(vals['total'] - vals['paid'], 2)}
            for name, vals in sorted(grouped.items())
        ]
        summary = {
            'orders': sum(r['orders'] for r in rows),
            'total': round(sum(r['total'] for r in rows), 2),
            'paid': round(sum(r['paid'] for r in rows), 2),
        }
        return Response({
            'columns': ['Revenue center', 'Orders', 'Subtotal', 'Tax', 'Discount', 'Total', 'Paid', 'Due'],
            'rows': rows,
            'summary': summary,
        })

    if kind == 'item-wise':
        grouped = defaultdict(lambda: {'qty': 0, 'amount': 0.0})
        items = OrderItem.objects.filter(
            order__tenant=tenant,
            order__created_at__date__gte=start,
            order__created_at__date__lte=end,
        ).exclude(order__status=OrderStatus.CANCELLED).select_related('menu_item')
        for line in items:
            name = line.menu_item.name if line.menu_item_id else 'Unknown'
            grouped[name]['qty'] += line.quantity or 0
            grouped[name]['amount'] += _money(line.total_price)
        rows = [
            {'item': name, 'qty': vals['qty'], 'amount': round(vals['amount'], 2)}
            for name, vals in sorted(grouped.items())
        ]
        return Response({
            'columns': ['Item', 'Qty', 'Amount'],
            'rows': rows,
            'summary': {
                'items': len(rows),
                'qty': sum(r['qty'] for r in rows),
                'amount': round(sum(r['amount'] for r in rows), 2),
            },
        })

    if kind == 'cancel':
        rows = []
        for order in _orders_in(tenant, start, end, include_cancelled=True).filter(status=OrderStatus.CANCELLED):
            rows.append({
                'date': (order.created_at or datetime.now()).date().isoformat(),
                'order_number': order.order_number,
                'customer': order.guest_name or '',
                'revenue_center': order.revenue_center or '',
                'total': _money(order.total_amount),
                'user': _uname(order.created_by),
            })
        return Response({
            'columns': ['Date', 'Order', 'Customer', 'Revenue center', 'Total', 'User'],
            'rows': rows,
            'summary': {'cancelled': len(rows), 'amount': round(sum(r['total'] for r in rows), 2)},
        })

    if kind == 'userwise-collection':
        grouped = defaultdict(lambda: {'sales_paid': 0.0, 'due_received': 0.0, 'orders': 0})
        for order in _orders_in(tenant, start, end):
            name = _uname(order.created_by)
            grouped[name]['sales_paid'] += _money(order.paid_amount)
            grouped[name]['orders'] += 1
        receives = PosDueReceive.objects.select_related('created_by').filter(
            tenant=tenant,
            receive_date__gte=start,
            receive_date__lte=end,
        )
        for rec in receives:
            name = _uname(rec.created_by)
            grouped[name]['due_received'] += _money(rec.amount)
        rows = [
            {
                'user': name,
                'orders': vals['orders'],
                'sales_paid': round(vals['sales_paid'], 2),
                'due_received': round(vals['due_received'], 2),
                'total': round(vals['sales_paid'] + vals['due_received'], 2),
            }
            for name, vals in sorted(grouped.items())
        ]
        return Response({
            'columns': ['User', 'Orders', 'Paid at sale', 'Due received', 'Total collection'],
            'rows': rows,
            'summary': {'collection': round(sum(r['total'] for r in rows), 2)},
        })

    if kind == 'expense':
        rows = []
        expenses = (
            FnbExpense.objects.select_related('head', 'head__category')
            .filter(tenant=tenant, expense_date__gte=start, expense_date__lte=end)
            .order_by('expense_date')
        )
        for row in expenses:
            rows.append({
                'date': row.expense_date.isoformat(),
                'category': row.head.category.name if row.head_id and row.head.category_id else '',
                'head': row.head.name if row.head_id else '',
                'revenue_center': row.revenue_center or '',
                'amount': _money(row.amount),
                'notes': row.notes or '',
            })
        return Response({
            'columns': ['Date', 'Category', 'Head', 'Revenue center', 'Amount', 'Notes'],
            'rows': rows,
            'summary': {'count': len(rows), 'amount': round(sum(r['amount'] for r in rows), 2)},
        })

    if kind == 'guest-status':
        stays = (
            Reservation.objects.select_related('guest', 'room')
            .filter(tenant=tenant, status=ReservationStatus.CHECKED_IN)
            .order_by('room__room_number')
        )
        rows = []
        for stay in stays:
            guest_name = f'{stay.guest.first_name} {stay.guest.last_name}'.strip() if stay.guest_id else ''
            orders = Order.objects.filter(tenant=tenant).exclude(status=OrderStatus.CANCELLED).filter(
                Q(reservation=stay) | Q(room_id=stay.room_id)
            )
            total = Decimal('0')
            paid = Decimal('0')
            count = 0
            for order in orders:
                count += 1
                total += order.total_amount or 0
                paid += order.paid_amount or 0
            rows.append({
                'room': stay.room.room_number if stay.room_id else '',
                'guest': guest_name,
                'reservation': stay.reservation_number,
                'check_in': stay.check_in_date.date().isoformat() if stay.check_in_date else '',
                'check_out': stay.check_out_date.date().isoformat() if stay.check_out_date else '',
                'orders': count,
                'fnb_total': _money(total),
                'fnb_paid': _money(paid),
                'fnb_due': _money(total - paid if total > paid else 0),
            })
        return Response({
            'columns': ['Room', 'Guest', 'Reservation', 'Check-in', 'Check-out', 'Orders', 'F&B total', 'Paid', 'Due'],
            'rows': rows,
            'summary': {
                'in_house': len(rows),
                'fnb_due': round(sum(r['fnb_due'] for r in rows), 2),
            },
        })

    return Response({'detail': f'Unknown report: {kind}'}, status=status.HTTP_400_BAD_REQUEST)
