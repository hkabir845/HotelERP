"""Banquet, CRM, HR operational records and workflow actions."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import Attendance, Employee, Payroll, PayrollStatus
from api.models.ops import OpsRecord
from api.views import deny_if_no_tenant

ACTION_STATUS = {
    'confirm': 'confirmed',
    'tentative': 'tentative',
    'start': 'in_progress',
    'complete': 'completed',
    'cancel': 'cancelled',
    'contact': 'contacted',
    'qualify': 'qualified',
    'convert': 'converted',
    'lose': 'lost',
    'send': 'sent',
    'accept': 'accepted',
    'reject': 'rejected',
    'invoice': 'invoiced',
    'void': 'void',
    'approve': 'approved',
    'disburse': 'disbursed',
    'close': 'closed',
    'pay': 'paid',
}


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    parsed = parse_datetime(str(value).replace('Z', '+00:00'))
    if parsed:
        return parsed
    day = parse_date(str(value)[:10])
    if day:
        return datetime.combine(day, datetime.min.time())
    return None


def _serialize(row):
    balance = float(row.amount or 0) - float(row.paid_amount or 0)
    return {
        'id': row.id,
        'kind': row.kind,
        'reference': row.reference,
        'title': row.title,
        'name': row.title,
        'contact_name': row.contact_name,
        'phone': row.phone,
        'email': row.email,
        'location': row.location,
        'code': row.reference,
        'scheduled_at': row.scheduled_at.isoformat() if row.scheduled_at else '',
        'quantity': float(row.quantity or 0),
        'amount': float(row.amount or 0),
        'paid_amount': float(row.paid_amount or 0),
        'balance': round(balance, 2),
        'status': row.status,
        'notes': row.notes,
        'extra': row.extra or {},
    }


def _normalize_kind(kind):
    kind = (kind or '').strip()
    aliases = {
        'banquet_events_new': 'banquet_event',
        'banquet_events': 'banquet_event',
        'banquet_pending-folios': 'banquet_event',
        'banquet_pending_folios': 'banquet_event',
        'banquet_pending_folio': 'banquet_event',
        'banquet_venue_forecast': 'banquet_event',
        'crm_quotations': 'crm_quotation',
        'crm_invoices': 'crm_invoice',
        'crm_leads': 'crm_lead',
        'crm_tasks': 'crm_task',
        'crm_feedback': 'crm_feedback',
        'crm_followup_task': 'crm_task',
        'crm_individual': 'crm_lead',
        'hr_leave': 'hr_leave',
        'hr_leave-requests': 'hr_leave',
        'hr_leave_request': 'hr_leave',
        'hr_loans': 'hr_loan',
        'hr_loan_approval': 'hr_loan',
        'hr_loans_approvals': 'hr_loan',
    }
    return aliases.get(kind, kind)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ops_records(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
    kind = _normalize_kind(request.query_params.get('kind') or (request.data or {}).get('kind'))
    if request.method == 'POST':
        data = request.data or {}
        title = (data.get('title') or data.get('name') or '').strip()
        if not title:
            return Response({'detail': 'title is required'}, status=status.HTTP_400_BAD_REQUEST)
        count = OpsRecord.objects.filter(tenant=tenant, kind=kind or 'record').count() + 1
        prefix = (kind or 'OPS').split('_')[-1][:3].upper()
        status_value = data.get('status') or 'open'
        if kind == 'banquet_event':
            status_value = data.get('status') or 'enquiry'
        elif kind == 'crm_lead':
            status_value = data.get('status') or 'new'
        elif kind in ('hr_leave', 'hr_loan'):
            status_value = data.get('status') or 'pending'
        elif kind == 'crm_quotation':
            status_value = data.get('status') or 'draft'
        elif kind == 'crm_invoice':
            status_value = data.get('status') or 'unpaid'
        row = OpsRecord.objects.create(
            tenant=tenant,
            kind=kind or 'record',
            reference=data.get('reference') or data.get('code') or f'{prefix}-{count:05d}',
            title=title,
            contact_name=data.get('contact_name') or '',
            phone=data.get('phone') or '',
            email=data.get('email') or '',
            location=data.get('location') or data.get('venue') or data.get('department') or '',
            scheduled_at=_dt(data.get('scheduled_at') or data.get('event_date') or data.get('date')),
            quantity=data.get('quantity') or data.get('pax') or 0,
            amount=data.get('amount') or 0,
            paid_amount=data.get('paid_amount') or 0,
            status=status_value,
            notes=data.get('notes') or '',
            extra={k: v for k, v in data.items() if k not in {
                'kind', 'title', 'name', 'reference', 'code', 'contact_name', 'phone', 'email',
                'location', 'venue', 'department', 'scheduled_at', 'event_date', 'date',
                'quantity', 'pax', 'amount', 'paid_amount', 'status', 'notes',
            }},
        )
        return Response(_serialize(row), status=status.HTTP_201_CREATED)
    qs = OpsRecord.objects.filter(tenant=tenant)
    if kind:
        qs = qs.filter(kind=kind)
    if kind == 'banquet_event' and 'pending' in (request.query_params.get('kind') or ''):
        pass
    pending = request.query_params.get('pending')
    items = [_serialize(r) for r in qs[:300]]
    if pending == '1':
        items = [i for i in items if i['balance'] > 0 and i['status'] not in ('cancelled', 'void', 'lost')]
    return Response({'items': items})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ops_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = OpsRecord.objects.get(pk=pk, tenant=tenant)
    except OpsRecord.DoesNotExist:
        return Response({'detail': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
    action = (request.data or {}).get('action') or ''
    if action == 'pay':
        extra = Decimal(str((request.data or {}).get('amount') or 0))
        if extra <= 0:
            extra = Decimal(str(row.amount or 0)) - Decimal(str(row.paid_amount or 0))
        if extra <= 0:
            return Response({'detail': 'Nothing due'}, status=status.HTTP_400_BAD_REQUEST)
        row.paid_amount = Decimal(str(row.paid_amount or 0)) + extra
        if row.paid_amount >= (row.amount or 0) and (row.amount or 0) > 0:
            row.status = 'paid' if row.kind in ('crm_invoice', 'hr_loan', 'banquet_event') else row.status
            if row.kind == 'banquet_event' and row.status not in ('cancelled',):
                pass
        note = (request.data or {}).get('notes') or ''
        if note:
            row.notes = (row.notes + '\n' if row.notes else '') + f'Payment {extra}: {note}'
        row.save()
        return Response(_serialize(row))
    if action not in ACTION_STATUS:
        return Response({'detail': f'Unknown action: {action}'}, status=status.HTTP_400_BAD_REQUEST)
    row.status = ACTION_STATUS[action]
    extra_note = (request.data or {}).get('notes')
    if extra_note:
        row.notes = (row.notes + '\n' if row.notes else '') + extra_note
    row.save()
    return Response(_serialize(row))


def _employee_item(emp):
    return {
        'id': emp.id,
        'employee_number': emp.employee_number,
        'title': emp.full_name,
        'name': emp.full_name,
        'first_name': emp.first_name,
        'last_name': emp.last_name,
        'contact_name': emp.full_name,
        'phone': emp.phone or emp.mobile or '',
        'email': emp.email or '',
        'location': emp.department or '',
        'department': emp.department or '',
        'designation': emp.designation or '',
        'amount': float(emp.salary or 0),
        'status': emp.status,
        'notes': emp.notes or '',
        'hire_date': emp.hire_date.isoformat() if emp.hire_date else '',
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def attendance(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    today = timezone.now().date()
    if request.method == 'POST':
        data = request.data or {}
        emp_id = data.get('employee_id') or data.get('id')
        if not emp_id:
            name = (data.get('title') or data.get('name') or '').strip()
            emp = Employee.objects.filter(tenant=tenant, first_name__icontains=name.split(' ')[0] if name else '').first()
            if not emp:
                return Response({'detail': 'Select an employee (employee_id)'}, status=status.HTTP_400_BAD_REQUEST)
            emp_id = emp.id
        try:
            emp = Employee.objects.get(id=emp_id, tenant=tenant)
        except Employee.DoesNotExist:
            return Response({'detail': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        action = (data.get('action') or 'punch_in').replace('-', '_')
        rec, _ = Attendance.objects.get_or_create(
            tenant=tenant,
            employee=emp,
            attendance_date=today,
            defaults={'status': 'present'},
        )
        now = timezone.now()
        if action == 'punch_out':
            rec.check_out = now
            if rec.check_in:
                rec.hours_worked = Decimal(str(round((now - rec.check_in).total_seconds() / 3600, 2)))
            rec.status = 'present'
        else:
            rec.check_in = rec.check_in or now
            rec.status = 'present'
        rec.notes = data.get('notes') or rec.notes
        rec.save()
        return Response(_attendance_item(rec), status=status.HTTP_201_CREATED)
    qs = Attendance.objects.select_related('employee').filter(tenant=tenant).order_by('-attendance_date', '-id')[:200]
    return Response({'items': [_attendance_item(r) for r in qs]})


def _attendance_item(rec):
    return {
        'id': rec.id,
        'employee_id': rec.employee_id,
        'title': rec.employee.full_name,
        'name': rec.employee.full_name,
        'reference': rec.employee.employee_number,
        'location': rec.employee.department or '',
        'scheduled_at': rec.attendance_date.isoformat(),
        'status': rec.status or ('in' if rec.check_in and not rec.check_out else 'complete' if rec.check_out else 'absent'),
        'notes': f"In: {rec.check_in.strftime('%H:%M') if rec.check_in else '-'}  Out: {rec.check_out.strftime('%H:%M') if rec.check_out else '-'}",
        'quantity': float(rec.hours_worked or 0),
        'amount': float(rec.overtime_hours or 0),
        'paid_amount': 0,
        'balance': 0,
        'phone': rec.employee.phone or '',
        'contact_name': rec.employee.full_name,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payroll(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if request.method == 'POST':
        data = request.data or {}
        emp_id = data.get('employee_id')
        emp = None
        if emp_id:
            emp = Employee.objects.filter(id=emp_id, tenant=tenant).first()
        if not emp:
            name = (data.get('title') or data.get('name') or data.get('contact_name') or '').strip()
            if name:
                emp = Employee.objects.filter(tenant=tenant, first_name__icontains=name.split()[0]).first()
        if not emp:
            return Response({'detail': 'Create an employee first, then generate payroll for them.'}, status=status.HTTP_400_BAD_REQUEST)
        start = parse_date(str(data.get('scheduled_at') or data.get('pay_period_start') or date.today().replace(day=1)))
        if not start:
            start = date.today().replace(day=1)
        end = parse_date(str(data.get('pay_period_end') or '')) or (start + timedelta(days=30))
        base = Decimal(str(data.get('amount') or emp.salary or 0))
        bonus = Decimal(str(data.get('bonus') or 0))
        tax = Decimal(str(data.get('tax') or 0))
        gross = base + bonus
        net = gross - tax
        n = Payroll.objects.filter(tenant=tenant).count() + 1
        row = Payroll.objects.create(
            tenant=tenant,
            payroll_number=f'PAY-{tenant.id}-{n:05d}',
            employee=emp,
            pay_period_start=start,
            pay_period_end=end,
            pay_date=end,
            base_salary=base,
            bonus=bonus,
            gross_pay=gross,
            tax=tax,
            total_deductions=tax,
            net_pay=net,
            status=PayrollStatus.DRAFT,
            notes=data.get('notes') or '',
            created_by=request.user,
        )
        return Response(_payroll_item(row), status=status.HTTP_201_CREATED)
    qs = Payroll.objects.select_related('employee').filter(tenant=tenant).order_by('-id')[:200]
    return Response({'items': [_payroll_item(r) for r in qs]})


def _payroll_item(row):
    return {
        'id': row.id,
        'title': row.employee.full_name,
        'name': row.employee.full_name,
        'reference': row.payroll_number,
        'contact_name': row.employee.full_name,
        'location': row.employee.department or '',
        'scheduled_at': row.pay_period_start.isoformat(),
        'amount': float(row.net_pay or 0),
        'paid_amount': float(row.net_pay or 0) if row.status == PayrollStatus.PAID else 0,
        'balance': 0 if row.status == PayrollStatus.PAID else float(row.net_pay or 0),
        'status': row.status,
        'notes': f'{row.pay_period_start} → {row.pay_period_end}  gross {row.gross_pay}',
        'phone': row.employee.phone or '',
        'quantity': float(row.hours_worked or 0),
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payroll_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = Payroll.objects.get(pk=pk, tenant=tenant)
    except Payroll.DoesNotExist:
        return Response({'detail': 'Payroll not found'}, status=status.HTTP_404_NOT_FOUND)
    action = (request.data or {}).get('action')
    now = timezone.now()
    if action == 'approve':
        row.status = PayrollStatus.APPROVED
        row.approved_by = request.user
        row.approved_at = now
    elif action == 'pay':
        row.status = PayrollStatus.PAID
        row.paid_by = request.user
        row.paid_at = now
        row.payment_method = (request.data or {}).get('payment_method') or 'bank'
    elif action == 'cancel':
        row.status = PayrollStatus.CANCELLED
    else:
        return Response({'detail': 'Use approve, pay, or cancel'}, status=status.HTTP_400_BAD_REQUEST)
    row.save()
    return Response(_payroll_item(row))
