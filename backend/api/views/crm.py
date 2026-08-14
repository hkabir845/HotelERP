"""CRM customers, leads, quotations, invoices, tasks, feedback, and reports."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import Guest, Reservation, ReservationStatus
from api.models.crm import (
    CrmComment,
    CrmCustomer,
    CrmFeedback,
    CrmInvoice,
    CrmInvoicePayment,
    CrmLead,
    CrmLeadSource,
    CrmQuotation,
    CrmTask,
)
from api.views import deny_if_no_tenant

LIVE_LEAD = ('new', 'contacted', 'qualified')


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


def _dt(value):
    if not value:
        return None
    raw = str(value).replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        day = _date(value)
        return datetime.combine(day, datetime.min.time()) if day else None


def _money(value):
    return float(value or 0)


def _fk(model, tenant, pk):
    if not pk:
        return None
    try:
        return model.objects.get(id=int(pk), tenant=tenant)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _opt(qs):
    return [{'id': row.id, 'name': row.name} for row in qs]


def _next(model, tenant, prefix):
    n = model.objects.filter(tenant=tenant).count() + 1
    return f'{prefix}-{tenant.id}-{n:05d}'


def _seed(tenant):
    if not CrmLeadSource.objects.filter(tenant=tenant).exists():
        for name in ('Walk-in', 'Website', 'Phone', 'Agent', 'Corporate'):
            CrmLeadSource.objects.create(tenant=tenant, name=name)


def _options(tenant):
    return {
        'lead_sources': _opt(CrmLeadSource.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'customers': _opt(CrmCustomer.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'leads': [{'id': r.id, 'name': f'{r.number} {r.name}'} for r in CrmLead.objects.filter(tenant=tenant).order_by('-id')[:100]],
        'payment_methods': [
            {'id': 'cash', 'name': 'Cash'},
            {'id': 'card', 'name': 'Card'},
            {'id': 'bank', 'name': 'Bank'},
            {'id': 'mobile', 'name': 'Mobile'},
        ],
    }


def serialize_source(row):
    return {
        'id': row.id,
        'name': row.name,
        'description': row.description or '',
        'is_active': row.is_active,
    }


def serialize_customer(row):
    return {
        'id': row.id,
        'kind': row.kind,
        'name': row.name,
        'company_name': row.company_name or '',
        'contact_person': row.contact_person or '',
        'phone': row.phone or '',
        'email': row.email or '',
        'address': row.address or '',
        'notes': row.notes or '',
        'is_active': row.is_active,
    }


def serialize_lead(row):
    return {
        'id': row.id,
        'number': row.number,
        'name': row.name,
        'phone': row.phone or '',
        'email': row.email or '',
        'company': row.company or '',
        'source_id': row.source_id,
        'source_name': row.source.name if row.source_id else '',
        'customer_id': row.customer_id,
        'expected_value': _money(row.expected_value),
        'next_followup': row.next_followup.isoformat() if row.next_followup else '',
        'status': row.status,
        'notes': row.notes or '',
        'can_contact': row.status == 'new',
        'can_qualify': row.status in ('new', 'contacted'),
        'can_convert': row.status in ('contacted', 'qualified'),
        'can_lose': row.status in LIVE_LEAD,
    }


def serialize_quote(row):
    return {
        'id': row.id,
        'number': row.number,
        'customer_id': row.customer_id,
        'lead_id': row.lead_id,
        'customer_name': row.customer_name,
        'phone': row.phone or '',
        'company': row.company or '',
        'valid_until': row.valid_until.isoformat() if row.valid_until else '',
        'amount': _money(row.amount),
        'status': row.status,
        'notes': row.notes or '',
        'can_send': row.status == 'draft',
        'can_accept': row.status == 'sent',
        'can_invoice': row.status in ('sent', 'accepted'),
        'can_reject': row.status in ('draft', 'sent'),
    }


def serialize_invoice(row):
    due = (row.amount or Decimal('0')) - (row.paid_amount or Decimal('0'))
    if due < 0:
        due = Decimal('0')
    return {
        'id': row.id,
        'number': row.number,
        'customer_id': row.customer_id,
        'customer_name': row.customer_name,
        'phone': row.phone or '',
        'due_date': row.due_date.isoformat() if row.due_date else '',
        'amount': _money(row.amount),
        'paid_amount': _money(row.paid_amount),
        'due': _money(due),
        'status': row.status,
        'notes': row.notes or '',
        'can_pay': row.status not in ('void', 'paid') and due > 0,
        'can_void': row.status in ('unpaid', 'sent', 'partial'),
    }


def serialize_task(row):
    return {
        'id': row.id,
        'title': row.title,
        'contact_name': row.contact_name or '',
        'phone': row.phone or '',
        'due_at': row.due_at.isoformat() if row.due_at else '',
        'is_followup': row.is_followup,
        'status': row.status,
        'notes': row.notes or '',
        'can_start': row.status == 'open',
        'can_complete': row.status in ('open', 'in_progress'),
        'can_cancel': row.status in ('open', 'in_progress'),
    }


def serialize_feedback(row):
    return {
        'id': row.id,
        'guest_name': row.guest_name,
        'place': row.place or '',
        'rating': row.rating,
        'comments': row.comments or '',
        'status': row.status,
        'can_review': row.status == 'open',
        'can_resolve': row.status in ('open', 'in_review'),
    }


def serialize_comment(row):
    return {
        'id': row.id,
        'related_kind': row.related_kind,
        'related_name': row.related_name or '',
        'body': row.body,
        'created_at': row.created_at.isoformat() if row.created_at else '',
        'created_by': (
            f'{row.created_by.first_name} {row.created_by.last_name}'.strip()
            or row.created_by.username
            if row.created_by_id
            else ''
        ),
    }


def _save_source(tenant, data, instance=None):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Name is required')
    row = instance or CrmLeadSource(tenant=tenant)
    row.name = name
    row.description = (data.get('description') or '').strip() or None
    if 'is_active' in data:
        row.is_active = _bool(data.get('is_active'))
    row.save()
    return row


def _save_customer(tenant, data, instance=None):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Name is required')
    row = instance or CrmCustomer(tenant=tenant)
    row.kind = (data.get('kind') or row.kind or 'individual').strip()
    row.name = name
    row.company_name = (data.get('company_name') or '').strip()
    row.contact_person = (data.get('contact_person') or '').strip()
    row.phone = (data.get('phone') or '').strip()
    row.email = (data.get('email') or '').strip()
    row.address = (data.get('address') or '').strip()
    row.notes = (data.get('notes') or '').strip()
    if 'is_active' in data:
        row.is_active = _bool(data.get('is_active'))
    row.save()
    return row


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def config_list(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    _seed(tenant)
    if kind == 'lead-sources':
        if request.method == 'POST':
            try:
                row = _save_source(tenant, request.data or {})
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=400)
            return Response(serialize_source(row), status=201)
        search = (request.query_params.get('search') or '').strip()
        qs = CrmLeadSource.objects.filter(tenant=tenant)
        if search:
            qs = qs.filter(name__icontains=search)
        return Response({'items': [serialize_source(r) for r in qs], 'options': _options(tenant)})
    if kind in ('customers', 'individuals', 'companies'):
        want = 'individual' if kind == 'individuals' else 'company' if kind == 'companies' else None
        if request.method == 'POST':
            data = dict(request.data or {})
            if want:
                data['kind'] = want
                if want == 'company' and not data.get('company_name'):
                    data['company_name'] = data.get('name')
            try:
                row = _save_customer(tenant, data)
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=400)
            return Response(serialize_customer(row), status=201)
        qs = CrmCustomer.objects.filter(tenant=tenant)
        if want:
            qs = qs.filter(kind=want)
        search = (request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search) | Q(company_name__icontains=search))
        return Response({'items': [serialize_customer(r) for r in qs[:400]], 'options': _options(tenant)})
    return Response({'detail': f'Unknown kind: {kind}'}, status=400)


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if kind == 'lead-sources':
        try:
            row = CrmLeadSource.objects.get(id=pk, tenant=tenant)
        except CrmLeadSource.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        if request.method == 'DELETE':
            row.delete()
            return Response(status=204)
        if request.method in ('PATCH', 'PUT'):
            try:
                row = _save_source(tenant, request.data or {}, instance=row)
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=400)
        return Response(serialize_source(row))
    if kind in ('customers', 'individuals', 'companies'):
        try:
            row = CrmCustomer.objects.get(id=pk, tenant=tenant)
        except CrmCustomer.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        if request.method == 'DELETE':
            row.delete()
            return Response(status=204)
        if request.method in ('PATCH', 'PUT'):
            try:
                row = _save_customer(tenant, request.data or {}, instance=row)
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=400)
        return Response(serialize_customer(row))
    return Response({'detail': f'Unknown kind: {kind}'}, status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def leads(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    _seed(tenant)
    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('name') or '').strip()
        if not name:
            return Response({'detail': 'Lead name is required'}, status=400)
        row = CrmLead.objects.create(
            tenant=tenant,
            number=_next(CrmLead, tenant, 'LD'),
            source=_fk(CrmLeadSource, tenant, data.get('source_id')),
            customer=_fk(CrmCustomer, tenant, data.get('customer_id')),
            name=name,
            phone=(data.get('phone') or '').strip(),
            email=(data.get('email') or '').strip(),
            company=(data.get('company') or '').strip(),
            expected_value=_dec(data.get('expected_value')),
            next_followup=_date(data.get('next_followup')),
            notes=(data.get('notes') or '').strip(),
            status='new',
        )
        return Response(serialize_lead(row), status=201)
    qs = CrmLead.objects.filter(tenant=tenant).select_related('source', 'customer')
    items = [serialize_lead(r) for r in qs[:400]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lead_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = CrmLead.objects.select_related('source', 'customer').get(id=pk, tenant=tenant)
    except CrmLead.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    if action == 'contact' and row.status == 'new':
        row.status = 'contacted'
    elif action == 'qualify' and row.status in ('new', 'contacted'):
        row.status = 'qualified'
    elif action == 'lose' and row.status in LIVE_LEAD:
        row.status = 'lost'
    elif action == 'convert' and row.status in ('contacted', 'qualified'):
        if not row.customer_id:
            kind = 'company' if row.company else 'individual'
            row.customer = CrmCustomer.objects.create(
                tenant=tenant,
                kind=kind,
                name=row.name,
                company_name=row.company,
                phone=row.phone,
                email=row.email,
            )
        row.status = 'converted'
    else:
        return Response({'detail': f'Cannot {action} this lead'}, status=400)
    row.save()
    return Response(serialize_lead(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quotations(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    _seed(tenant)
    if request.method == 'POST':
        data = request.data or {}
        customer = _fk(CrmCustomer, tenant, data.get('customer_id'))
        name = (data.get('customer_name') or (customer.name if customer else '')).strip()
        if not name:
            return Response({'detail': 'Customer is required'}, status=400)
        row = CrmQuotation.objects.create(
            tenant=tenant,
            number=_next(CrmQuotation, tenant, 'QT'),
            customer=customer,
            lead=_fk(CrmLead, tenant, data.get('lead_id')),
            customer_name=name,
            phone=(data.get('phone') or (customer.phone if customer else '')).strip(),
            company=(data.get('company') or (customer.company_name if customer else '')).strip(),
            valid_until=_date(data.get('valid_until')),
            amount=_dec(data.get('amount')),
            notes=(data.get('notes') or '').strip(),
            status='draft',
        )
        return Response(serialize_quote(row), status=201)
    items = [serialize_quote(r) for r in CrmQuotation.objects.filter(tenant=tenant).select_related('customer')[:400]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quotation_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = CrmQuotation.objects.get(id=pk, tenant=tenant)
    except CrmQuotation.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    if action == 'send' and row.status == 'draft':
        row.status = 'sent'
        row.save()
    elif action == 'accept' and row.status == 'sent':
        row.status = 'accepted'
        row.save()
    elif action == 'reject' and row.status in ('draft', 'sent'):
        row.status = 'rejected'
        row.save()
    elif action == 'invoice' and row.status in ('sent', 'accepted'):
        inv = CrmInvoice.objects.create(
            tenant=tenant,
            number=_next(CrmInvoice, tenant, 'INV'),
            customer=row.customer,
            quotation=row,
            customer_name=row.customer_name,
            phone=row.phone,
            due_date=date.today() + timedelta(days=15),
            amount=row.amount,
            status='unpaid',
            notes=f'From quotation {row.number}',
        )
        row.status = 'invoiced'
        row.save()
        return Response({'quotation': serialize_quote(row), 'invoice': serialize_invoice(inv)})
    else:
        return Response({'detail': f'Cannot {action} this quotation'}, status=400)
    return Response(serialize_quote(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def invoices(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    _seed(tenant)
    if request.method == 'POST':
        data = request.data or {}
        customer = _fk(CrmCustomer, tenant, data.get('customer_id'))
        name = (data.get('customer_name') or (customer.name if customer else '')).strip()
        if not name:
            return Response({'detail': 'Customer is required'}, status=400)
        row = CrmInvoice.objects.create(
            tenant=tenant,
            number=_next(CrmInvoice, tenant, 'INV'),
            customer=customer,
            customer_name=name,
            phone=(data.get('phone') or (customer.phone if customer else '')).strip(),
            due_date=_date(data.get('due_date')),
            amount=_dec(data.get('amount')),
            notes=(data.get('notes') or '').strip(),
            status='unpaid',
        )
        return Response(serialize_invoice(row), status=201)
    items = [serialize_invoice(r) for r in CrmInvoice.objects.filter(tenant=tenant)[:400]]
    return Response({
        'items': items,
        'options': _options(tenant),
        'summary': {
            'invoices': len(items),
            'due': round(sum(r['due'] for r in items), 2),
        },
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invoice_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = CrmInvoice.objects.get(id=pk, tenant=tenant)
    except CrmInvoice.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    data = request.data or {}
    if action == 'void' and row.status in ('unpaid', 'sent', 'partial'):
        row.status = 'void'
        row.save()
        return Response(serialize_invoice(row))
    if action == 'pay':
        amount = _dec(data.get('amount'))
        due = row.amount - row.paid_amount
        if amount <= 0:
            amount = due
        if amount > due:
            return Response({'detail': 'Amount exceeds invoice due'}, status=400)
        CrmInvoicePayment.objects.create(
            invoice=row,
            pay_date=_date(data.get('pay_date')) or date.today(),
            amount=amount,
            method=(data.get('method') or 'cash').strip() or 'cash',
            notes=(data.get('notes') or '').strip(),
        )
        row.paid_amount += amount
        row.status = 'paid' if row.paid_amount >= row.amount else 'partial'
        row.save()
        return Response(serialize_invoice(row))
    return Response({'detail': f'Cannot {action} this invoice'}, status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tasks(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        title = (data.get('title') or '').strip()
        if not title:
            return Response({'detail': 'Task is required'}, status=400)
        row = CrmTask.objects.create(
            tenant=tenant,
            title=title,
            contact_name=(data.get('contact_name') or '').strip(),
            phone=(data.get('phone') or '').strip(),
            due_at=_dt(data.get('due_at')),
            is_followup=_bool(data.get('is_followup'), False),
            notes=(data.get('notes') or '').strip(),
            status='open',
        )
        return Response(serialize_task(row), status=201)
    qs = CrmTask.objects.filter(tenant=tenant)
    followup = str(request.query_params.get('followup') or '') in ('1', 'true')
    if followup:
        qs = qs.filter(Q(is_followup=True) | Q(status='open'))
    items = [serialize_task(r) for r in qs[:400]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = CrmTask.objects.get(id=pk, tenant=tenant)
    except CrmTask.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    if action == 'start' and row.status == 'open':
        row.status = 'in_progress'
    elif action == 'complete' and row.status in ('open', 'in_progress'):
        row.status = 'completed'
    elif action == 'cancel' and row.status in ('open', 'in_progress'):
        row.status = 'cancelled'
    else:
        return Response({'detail': f'Cannot {action} this task'}, status=400)
    row.save()
    return Response(serialize_task(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def feedback(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        name = (data.get('guest_name') or '').strip()
        if not name:
            return Response({'detail': 'Guest name is required'}, status=400)
        rating = int(data.get('rating') or 5)
        rating = min(5, max(1, rating))
        row = CrmFeedback.objects.create(
            tenant=tenant,
            guest_name=name,
            place=(data.get('place') or '').strip(),
            rating=rating,
            comments=(data.get('comments') or '').strip(),
            status='open',
        )
        return Response(serialize_feedback(row), status=201)
    items = [serialize_feedback(r) for r in CrmFeedback.objects.filter(tenant=tenant)[:400]]
    return Response({'items': items})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def feedback_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = CrmFeedback.objects.get(id=pk, tenant=tenant)
    except CrmFeedback.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    if action == 'review':
        row.status = 'in_review'
    elif action == 'resolve':
        row.status = 'resolved'
    else:
        return Response({'detail': f'Cannot {action} this feedback'}, status=400)
    row.save()
    return Response(serialize_feedback(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comments(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        body = (data.get('body') or '').strip()
        if not body:
            return Response({'detail': 'Comment is required'}, status=400)
        row = CrmComment.objects.create(
            tenant=tenant,
            related_kind=(data.get('related_kind') or 'lead').strip(),
            related_name=(data.get('related_name') or '').strip(),
            body=body,
            created_by=request.user,
        )
        return Response(serialize_comment(row), status=201)
    items = [serialize_comment(r) for r in CrmComment.objects.filter(tenant=tenant).select_related('created_by')[:400]]
    return Response({'items': items})


def _period(request):
    start = _date(request.query_params.get('from')) or date.today().replace(day=1)
    end = _date(request.query_params.get('to')) or date.today()
    if end < start:
        start, end = end, start
    return start, end


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crm_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    start, end = _period(request)

    if kind == 'leads':
        qs = CrmLead.objects.filter(tenant=tenant, created_at__date__gte=start, created_at__date__lte=end)
        by_status = defaultdict(lambda: {'count': 0, 'value': 0.0})
        by_source = defaultdict(lambda: {'count': 0, 'value': 0.0})
        for row in qs.select_related('source'):
            by_status[row.status]['count'] += 1
            by_status[row.status]['value'] += _money(row.expected_value)
            src = row.source.name if row.source_id else 'Unspecified'
            by_source[src]['count'] += 1
            by_source[src]['value'] += _money(row.expected_value)
        rows = [{'source': k, 'leads': v['count'], 'value': round(v['value'], 2)} for k, v in sorted(by_source.items())]
        return Response({
            'columns': ['Source', 'Leads', 'Expected value'],
            'rows': rows,
            'summary': {
                'leads': qs.count(),
                'new': by_status['new']['count'],
                'converted': by_status['converted']['count'],
                'lost': by_status['lost']['count'],
                'pipeline': round(sum(v['value'] for v in by_status.values()), 2),
            },
        })

    if kind == 'guests':
        qs = Reservation.objects.filter(tenant=tenant, check_in_date__date__lte=end, check_out_date__date__gte=start)
        qs = qs.exclude(status__in=(ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW))
        by_guest = defaultdict(lambda: {'stays': 0, 'nights': 0, 'phone': ''})
        for res in qs.select_related('guest'):
            name = res.guest.full_name if res.guest_id else 'Unknown'
            nights = max(1, (res.check_out_date.date() - res.check_in_date.date()).days)
            by_guest[name]['stays'] += 1
            by_guest[name]['nights'] += nights
            by_guest[name]['phone'] = (res.guest.phone or res.guest.mobile or '') if res.guest_id else ''
        rows = [
            {'guest': name, 'stays': val['stays'], 'nights': val['nights'], 'phone': val['phone']}
            for name, val in sorted(by_guest.items(), key=lambda kv: -kv[1]['stays'])
        ]
        return Response({
            'columns': ['Guest', 'Stays', 'Nights', 'Phone'],
            'rows': rows,
            'summary': {'guests': len(rows), 'stays': sum(r['stays'] for r in rows)},
        })

    if kind == 'checklists':
        open_tasks = CrmTask.objects.filter(tenant=tenant, status__in=('open', 'in_progress'))
        overdue = [
            {
                'task': t.title,
                'contact': t.contact_name,
                'due': t.due_at.date().isoformat() if t.due_at else '',
                'status': t.status,
                'followup': 'Yes' if t.is_followup else 'No',
            }
            for t in open_tasks.order_by('due_at')
        ]
        leads = CrmLead.objects.filter(tenant=tenant, status__in=LIVE_LEAD, next_followup__isnull=False)
        for lead in leads:
            overdue.append({
                'task': f'Follow up {lead.name}',
                'contact': lead.phone,
                'due': lead.next_followup.isoformat(),
                'status': lead.status,
                'followup': 'Yes',
            })
        overdue.sort(key=lambda r: r['due'] or '9999')
        return Response({
            'columns': ['Task', 'Contact', 'Due', 'Status', 'Follow-up'],
            'rows': overdue,
            'summary': {'open': len(overdue)},
        })

    if kind == 'guest-frequency':
        qs = Reservation.objects.filter(tenant=tenant).exclude(
            status__in=(ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW)
        ).filter(check_in_date__date__gte=start, check_in_date__date__lte=end)
        grouped = defaultdict(int)
        for res in qs.select_related('guest'):
            name = res.guest.full_name if res.guest_id else 'Unknown'
            grouped[name] += 1
        rows = [{'guest': name, 'visits': count} for name, count in sorted(grouped.items(), key=lambda kv: -kv[1])]
        repeat = sum(1 for r in rows if r['visits'] > 1)
        return Response({
            'columns': ['Guest', 'Visits'],
            'rows': rows,
            'summary': {'guests': len(rows), 'repeat': repeat},
        })

    return Response({'detail': f'Unknown report: {kind}'}, status=400)
