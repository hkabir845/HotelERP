"""HR masters, employees, attendance, leave, loans, payroll, and reports."""
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import Attendance, Employee, EmploymentStatus, Payroll, PayrollStatus
from api.models.hr import (
    HrBranch,
    HrDepartment,
    HrDesignation,
    HrHoliday,
    HrLeaveRequest,
    HrLeaveType,
    HrLoan,
    HrSalaryStructure,
    HrSettings,
    HrWorkShift,
)
from api.services.hotel_gl import post_payroll_accrual, post_payroll_payment, reverse_payroll_accrual
from api.views import deny_if_no_tenant

SIMPLE = {
    'branches': HrBranch,
    'departments': HrDepartment,
    'designations': HrDesignation,
    'work-shifts': HrWorkShift,
    'leave-types': HrLeaveType,
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


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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


def _money(value):
    return float(value or 0)


def _fk(model, tenant, pk):
    if not pk:
        return None
    try:
        return model.objects.get(id=int(pk), tenant=tenant)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _emp(tenant, pk):
    if not pk:
        return None
    try:
        return Employee.objects.get(id=int(pk), tenant=tenant)
    except (Employee.DoesNotExist, TypeError, ValueError):
        return None


def _opt(qs):
    return [{'id': row.id, 'name': getattr(row, 'name', str(row.id))} for row in qs]


def _parse_hhmm(value, fallback=time(9, 0)):
    raw = (value or '').strip()
    try:
        parts = raw.split(':')
        return time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    except (TypeError, ValueError, IndexError):
        return fallback


def _settings(tenant):
    row, _ = HrSettings.objects.get_or_create(tenant=tenant)
    return row


def _seed(tenant):
    if not HrBranch.objects.filter(tenant=tenant).exists():
        HrBranch.objects.create(tenant=tenant, name='Head Office')
    if not HrDepartment.objects.filter(tenant=tenant).exists():
        for name in ('Front Office', 'Housekeeping', 'F&B', 'Accounts', 'HR'):
            HrDepartment.objects.create(tenant=tenant, name=name)
    if not HrDesignation.objects.filter(tenant=tenant).exists():
        for name in ('Manager', 'Supervisor', 'Executive', 'Associate'):
            HrDesignation.objects.create(tenant=tenant, name=name)
    if not HrWorkShift.objects.filter(tenant=tenant).exists():
        HrWorkShift.objects.create(tenant=tenant, name='Morning', start_time='09:00', end_time='17:00')
        HrWorkShift.objects.create(tenant=tenant, name='Evening', start_time='14:00', end_time='22:00')
        HrWorkShift.objects.create(tenant=tenant, name='Night', start_time='22:00', end_time='06:00')
    if not HrLeaveType.objects.filter(tenant=tenant).exists():
        HrLeaveType.objects.create(tenant=tenant, name='Casual', days_per_year=10, is_paid=True)
        HrLeaveType.objects.create(tenant=tenant, name='Sick', days_per_year=14, is_paid=True)
        HrLeaveType.objects.create(tenant=tenant, name='Annual', days_per_year=20, is_paid=True)
        HrLeaveType.objects.create(tenant=tenant, name='Unpaid', days_per_year=0, is_paid=False)
    _settings(tenant)


def _options(tenant):
    return {
        'branches': _opt(HrBranch.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'departments': _opt(HrDepartment.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'designations': _opt(HrDesignation.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'work_shifts': _opt(HrWorkShift.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'leave_types': _opt(HrLeaveType.objects.filter(tenant=tenant, is_active=True).order_by('name')),
        'employees': [
            {'id': e.id, 'name': e.full_name}
            for e in Employee.objects.filter(tenant=tenant, status=EmploymentStatus.ACTIVE).order_by('first_name')
        ],
        'employment_statuses': [
            {'id': 'active', 'name': 'Active'},
            {'id': 'inactive', 'name': 'Inactive'},
            {'id': 'terminated', 'name': 'Terminated'},
            {'id': 'on_leave', 'name': 'On leave'},
        ],
        'payment_methods': [
            {'id': 'cash', 'name': 'Cash'},
            {'id': 'bank', 'name': 'Bank'},
            {'id': 'mobile', 'name': 'Mobile'},
        ],
    }


def serialize_named(kind, row):
    data = {
        'id': row.id,
        'name': row.name,
        'description': getattr(row, 'description', None) or '',
        'is_active': getattr(row, 'is_active', True),
    }
    if kind == 'work-shifts':
        data.update({
            'start_time': row.start_time or '',
            'end_time': row.end_time or '',
            'grace_minutes': row.grace_minutes,
        })
    elif kind == 'leave-types':
        data.update({'days_per_year': row.days_per_year, 'is_paid': row.is_paid})
    return data


def serialize_holiday(row):
    return {
        'id': row.id,
        'name': row.name,
        'holiday_date': row.holiday_date.isoformat() if row.holiday_date else '',
        'description': row.description or '',
        'is_active': row.is_active,
    }


def serialize_employee(row):
    return {
        'id': row.id,
        'employee_number': row.employee_number,
        'first_name': row.first_name,
        'last_name': row.last_name,
        'name': row.full_name,
        'phone': row.phone or '',
        'mobile': row.mobile or '',
        'email': row.email or '',
        'branch': row.branch or '',
        'department': row.department or '',
        'designation': row.designation or '',
        'work_shift': row.work_shift or '',
        'salary': _money(row.salary),
        'hire_date': row.hire_date.isoformat() if row.hire_date else '',
        'status': row.status,
        'bank_name': row.bank_name or '',
        'bank_account': row.bank_account or '',
        'notes': row.notes or '',
    }


def serialize_structure(row):
    return {
        'id': row.id,
        'employee_id': row.employee_id,
        'employee_name': row.employee.full_name,
        'basic': _money(row.basic),
        'house_rent': _money(row.house_rent),
        'medical': _money(row.medical),
        'conveyance': _money(row.conveyance),
        'other_allowance': _money(row.other_allowance),
        'tax_percent': _money(row.tax_percent),
        'gross': _money(row.gross),
    }


def serialize_leave(row):
    return {
        'id': row.id,
        'employee_id': row.employee_id,
        'employee_name': row.employee.full_name,
        'leave_type_id': row.leave_type_id,
        'leave_type': row.leave_type.name if row.leave_type_id else '',
        'date_from': row.date_from.isoformat(),
        'date_to': row.date_to.isoformat(),
        'days': float(row.days or 0),
        'reason': row.reason or '',
        'status': row.status,
        'can_approve': row.status == 'pending',
        'can_reject': row.status == 'pending',
    }


def serialize_loan(row):
    due = (row.amount or Decimal('0')) - (row.paid_amount or Decimal('0'))
    if due < 0:
        due = Decimal('0')
    return {
        'id': row.id,
        'number': row.number,
        'employee_id': row.employee_id,
        'employee_name': row.employee.full_name,
        'amount': _money(row.amount),
        'installments': row.installments,
        'paid_amount': _money(row.paid_amount),
        'due': _money(due),
        'request_date': row.request_date.isoformat(),
        'purpose': row.purpose or '',
        'status': row.status,
        'can_approve': row.status == 'pending',
        'can_disburse': row.status == 'approved',
        'can_repay': row.status == 'disbursed' and due > 0,
        'can_reject': row.status == 'pending',
        'can_close': row.status in ('disbursed', 'paid') and due <= 0,
    }


def serialize_attendance(row):
    return {
        'id': row.id,
        'employee_id': row.employee_id,
        'employee_name': row.employee.full_name,
        'employee_number': row.employee.employee_number,
        'department': row.employee.department or '',
        'attendance_date': row.attendance_date.isoformat(),
        'check_in': row.check_in.strftime('%H:%M') if row.check_in else '',
        'check_out': row.check_out.strftime('%H:%M') if row.check_out else '',
        'hours_worked': _money(row.hours_worked),
        'late_minutes': _money(row.late_minutes),
        'late_fine': _money(row.late_fine),
        'status': row.status or '',
        'notes': row.notes or '',
        'can_punch_out': bool(row.check_in and not row.check_out),
    }


def serialize_payroll(row):
    return {
        'id': row.id,
        'payroll_number': row.payroll_number,
        'employee_id': row.employee_id,
        'employee_name': row.employee.full_name,
        'department': row.employee.department or '',
        'pay_period_start': row.pay_period_start.isoformat(),
        'pay_period_end': row.pay_period_end.isoformat(),
        'pay_date': row.pay_date.isoformat() if row.pay_date else '',
        'base_salary': _money(row.base_salary),
        'allowances': _money(row.allowances),
        'bonus': _money(row.bonus),
        'gross_pay': _money(row.gross_pay),
        'late_fine': _money(row.other_deductions),
        'tax': _money(row.tax),
        'total_deductions': _money(row.total_deductions),
        'net_pay': _money(row.net_pay),
        'status': row.status,
        'payment_method': row.payment_method or '',
        'accrual_journal_id': row.accrual_journal_id,
        'payment_journal_id': row.payment_journal_id,
        'can_approve': row.status in (PayrollStatus.DRAFT, PayrollStatus.PENDING),
        'can_pay': row.status == PayrollStatus.APPROVED,
        'can_cancel': row.status in (PayrollStatus.DRAFT, PayrollStatus.PENDING, PayrollStatus.APPROVED),
    }


def _apply_named(kind, row, data):
    name = (data.get('name') or '').strip()
    if not name:
        raise ValueError('Name is required')
    row.name = name
    row.description = (data.get('description') or '').strip() or None
    if 'is_active' in data:
        row.is_active = _bool(data.get('is_active'))
    if kind == 'work-shifts':
        row.start_time = (data.get('start_time') or '09:00').strip()
        row.end_time = (data.get('end_time') or '18:00').strip()
        row.grace_minutes = max(0, _int(data.get('grace_minutes'), 15))
    elif kind == 'leave-types':
        row.days_per_year = max(0, _int(data.get('days_per_year'), 0))
        row.is_paid = _bool(data.get('is_paid'), True)
    row.save()
    return row


def _save_employee(tenant, data, instance=None):
    first = (data.get('first_name') or '').strip()
    last = (data.get('last_name') or '').strip()
    if not first:
        raise ValueError('First name is required')
    row = instance or Employee(tenant=tenant)
    if not instance:
        n = Employee.objects.filter(tenant=tenant).count() + 1
        row.employee_number = (data.get('employee_number') or '').strip() or f'EMP-{tenant.id}-{n:05d}'
        row.hire_date = _date(data.get('hire_date')) or date.today()
    elif data.get('hire_date'):
        row.hire_date = _date(data.get('hire_date')) or row.hire_date
    row.first_name = first
    row.last_name = last or '-'
    row.email = (data.get('email') or '').strip() or None
    row.phone = (data.get('phone') or '').strip() or None
    row.mobile = (data.get('mobile') or '').strip() or None
    row.branch = (data.get('branch') or '').strip() or None
    row.department = (data.get('department') or '').strip() or None
    row.designation = (data.get('designation') or '').strip() or None
    row.work_shift = (data.get('work_shift') or '').strip() or None
    row.salary = _dec(data.get('salary')) if data.get('salary') not in (None, '') else row.salary
    row.status = (data.get('status') or row.status or EmploymentStatus.ACTIVE)
    row.bank_name = (data.get('bank_name') or '').strip() or None
    row.bank_account = (data.get('bank_account') or '').strip() or None
    row.notes = (data.get('notes') or '').strip() or None
    row.save()
    return row


def _save_structure(tenant, data, instance=None):
    emp = instance.employee if instance else _emp(tenant, data.get('employee_id'))
    if not emp:
        raise ValueError('Employee is required')
    row = instance or HrSalaryStructure.objects.filter(tenant=tenant, employee=emp).first()
    if not row:
        row = HrSalaryStructure(tenant=tenant, employee=emp)
    row.basic = _dec(data.get('basic'))
    row.house_rent = _dec(data.get('house_rent'))
    row.medical = _dec(data.get('medical'))
    row.conveyance = _dec(data.get('conveyance'))
    row.other_allowance = _dec(data.get('other_allowance'))
    row.tax_percent = _dec(data.get('tax_percent'))
    row.save()
    if not emp.salary:
        emp.salary = row.gross
        emp.save(update_fields=['salary'])
    return row


def _save_holiday(tenant, data, instance=None):
    name = (data.get('name') or '').strip()
    day = _date(data.get('holiday_date'))
    if not name or not day:
        raise ValueError('Name and date are required')
    row = instance or HrHoliday(tenant=tenant)
    row.name = name
    row.holiday_date = day
    row.description = (data.get('description') or '').strip() or None
    if 'is_active' in data:
        row.is_active = _bool(data.get('is_active'))
    row.save()
    return row


def serialize_kind(kind, row):
    if kind == 'employees':
        return serialize_employee(row)
    if kind == 'holidays':
        return serialize_holiday(row)
    if kind == 'salary-structures':
        return serialize_structure(row)
    return serialize_named(kind, row)


def _list_qs(kind, tenant):
    if kind in SIMPLE:
        return SIMPLE[kind].objects.filter(tenant=tenant).order_by('name')
    if kind == 'employees':
        return Employee.objects.filter(tenant=tenant).order_by('first_name', 'last_name')
    if kind == 'holidays':
        return HrHoliday.objects.filter(tenant=tenant).order_by('holiday_date')
    if kind == 'salary-structures':
        return HrSalaryStructure.objects.filter(tenant=tenant).select_related('employee').order_by('employee__first_name')
    return None


def _create_or_update(kind, tenant, data, instance=None):
    if kind in SIMPLE:
        row = instance or SIMPLE[kind](tenant=tenant)
        return _apply_named(kind, row, data)
    if kind == 'employees':
        return _save_employee(tenant, data, instance)
    if kind == 'holidays':
        return _save_holiday(tenant, data, instance)
    if kind == 'salary-structures':
        return _save_structure(tenant, data, instance)
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
    _seed(tenant)
    qs = _list_qs(kind, tenant)
    if qs is None:
        return Response({'detail': f'Unknown kind: {kind}'}, status=400)
    if request.method == 'POST':
        try:
            row = _create_or_update(kind, tenant, request.data or {})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_kind(kind, row), status=201)
    search = (request.query_params.get('search') or '').strip()
    department = (request.query_params.get('department') or '').strip()
    if kind == 'employees' and department:
        qs = qs.filter(department__icontains=department)
    if search:
        if kind == 'employees':
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(employee_number__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
                | Q(department__icontains=search)
                | Q(designation__icontains=search)
            )
        elif hasattr(qs.model, 'name'):
            qs = qs.filter(name__icontains=search)
    items = [serialize_kind(kind, row) for row in qs[:500]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def config_detail(request, kind, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    qs = _list_qs(kind, tenant)
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
            row = _create_or_update(kind, tenant, request.data or {}, instance=row)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(serialize_kind(kind, row))
    return Response(serialize_kind(kind, row))


def _shift_for(emp, settings):
    if emp.work_shift:
        shift = HrWorkShift.objects.filter(tenant=emp.tenant, name=emp.work_shift, is_active=True).first()
        if shift:
            return _parse_hhmm(shift.start_time), shift.grace_minutes
    return _parse_hhmm(settings.work_start), settings.late_grace_minutes


def _apply_late(rec, settings):
    if not rec.check_in:
        rec.late_minutes = 0
        rec.late_fine = 0
        return
    start, grace = _shift_for(rec.employee, settings)
    local = timezone.localtime(rec.check_in)
    start_dt = datetime.combine(rec.attendance_date, start)
    if timezone.is_aware(rec.check_in):
        start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
    delta = (local - start_dt).total_seconds() / 60
    late = max(0, delta - grace)
    rec.late_minutes = Decimal(str(round(late, 2)))
    rec.late_fine = settings.late_fine_amount if late > 0 else Decimal('0')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def attendance(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    _seed(tenant)
    settings = _settings(tenant)
    if request.method == 'POST':
        data = request.data or {}
        emp = _emp(tenant, data.get('employee_id'))
        if not emp:
            return Response({'detail': 'Select an employee'}, status=400)
        day = _date(data.get('attendance_date')) or timezone.localdate()
        rec, _ = Attendance.objects.get_or_create(
            tenant=tenant, employee=emp, attendance_date=day, defaults={'status': 'present'}
        )
        now = timezone.now()
        action = (data.get('action') or 'punch_in').replace('-', '_')
        if action == 'punch_out':
            if not rec.check_in:
                return Response({'detail': 'Punch in first'}, status=400)
            rec.check_out = now
            rec.hours_worked = Decimal(str(round((now - rec.check_in).total_seconds() / 3600, 2)))
            rec.status = 'present'
        else:
            if rec.check_in and not rec.check_out:
                return Response({'detail': 'Already punched in'}, status=400)
            rec.check_in = rec.check_in or now
            rec.status = 'present'
            _apply_late(rec, settings)
        rec.notes = data.get('notes') or rec.notes
        rec.save()
        return Response(serialize_attendance(rec), status=201)
    qs = Attendance.objects.select_related('employee').filter(tenant=tenant).order_by('-attendance_date', '-id')
    start = _date(request.query_params.get('from'))
    end = _date(request.query_params.get('to'))
    if start:
        qs = qs.filter(attendance_date__gte=start)
    if end:
        qs = qs.filter(attendance_date__lte=end)
    items = [serialize_attendance(r) for r in qs[:400]]
    return Response({'items': items, 'options': _options(tenant), 'today': timezone.localdate().isoformat()})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def leaves(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    _seed(tenant)
    if request.method == 'POST':
        data = request.data or {}
        emp = _emp(tenant, data.get('employee_id'))
        if not emp:
            return Response({'detail': 'Employee is required'}, status=400)
        start = _date(data.get('date_from'))
        end = _date(data.get('date_to')) or start
        if not start:
            return Response({'detail': 'From date is required'}, status=400)
        if end < start:
            start, end = end, start
        days = _dec(data.get('days'), str((end - start).days + 1))
        row = HrLeaveRequest.objects.create(
            tenant=tenant,
            employee=emp,
            leave_type=_fk(HrLeaveType, tenant, data.get('leave_type_id')),
            date_from=start,
            date_to=end,
            days=days,
            reason=(data.get('reason') or '').strip(),
            status='pending',
        )
        return Response(serialize_leave(row), status=201)
    qs = HrLeaveRequest.objects.filter(tenant=tenant).select_related('employee', 'leave_type')
    items = [serialize_leave(r) for r in qs[:400]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = HrLeaveRequest.objects.select_related('employee', 'leave_type').get(id=pk, tenant=tenant)
    except HrLeaveRequest.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    if action not in ('approve', 'reject') or row.status != 'pending':
        return Response({'detail': 'Only pending leave can be approved or rejected'}, status=400)
    row.status = 'approved' if action == 'approve' else 'rejected'
    row.decided_by = request.user
    row.decided_at = timezone.now()
    row.save()
    return Response(serialize_leave(row))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def loans(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    _seed(tenant)
    if request.method == 'POST':
        data = request.data or {}
        emp = _emp(tenant, data.get('employee_id'))
        amount = _dec(data.get('amount'))
        if not emp or amount <= 0:
            return Response({'detail': 'Employee and amount are required'}, status=400)
        n = HrLoan.objects.filter(tenant=tenant).count() + 1
        row = HrLoan.objects.create(
            tenant=tenant,
            number=f'LN-{tenant.id}-{n:05d}',
            employee=emp,
            amount=amount,
            installments=max(1, _int(data.get('installments'), 1)),
            request_date=_date(data.get('request_date')) or date.today(),
            purpose=(data.get('purpose') or '').strip(),
            status='pending',
        )
        return Response(serialize_loan(row), status=201)
    qs = HrLoan.objects.filter(tenant=tenant).select_related('employee')
    pending = str(request.query_params.get('pending') or '') in ('1', 'true')
    if pending:
        qs = qs.filter(status='pending')
    items = [serialize_loan(r) for r in qs[:400]]
    return Response({'items': items, 'options': _options(tenant)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loan_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = HrLoan.objects.select_related('employee').get(id=pk, tenant=tenant)
    except HrLoan.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    data = request.data or {}
    if action == 'approve' and row.status == 'pending':
        row.status = 'approved'
    elif action == 'reject' and row.status == 'pending':
        row.status = 'rejected'
    elif action == 'disburse' and row.status == 'approved':
        row.status = 'disbursed'
    elif action == 'repay' and row.status == 'disbursed':
        extra = _dec(data.get('amount'))
        due = row.amount - row.paid_amount
        if extra <= 0:
            extra = due
        if extra > due:
            return Response({'detail': 'Amount exceeds loan due'}, status=400)
        row.paid_amount += extra
        if row.paid_amount >= row.amount:
            row.status = 'paid'
    elif action == 'close' and row.status in ('disbursed', 'paid'):
        row.status = 'closed'
    else:
        return Response({'detail': f'Cannot {action} this loan'}, status=400)
    row.save()
    return Response(serialize_loan(row))


def _structure_amounts(emp):
    try:
        struct = emp.salary_structure
    except HrSalaryStructure.DoesNotExist:
        struct = None
    if struct:
        return struct.gross, struct.house_rent + struct.medical + struct.conveyance + struct.other_allowance, struct.tax_percent
    return emp.salary or Decimal('0'), Decimal('0'), Decimal('0')


def _generate_payroll(tenant, emp, start, end, user):
    existing = Payroll.objects.filter(
        tenant=tenant, employee=emp, pay_period_start=start, pay_period_end=end
    ).exclude(status=PayrollStatus.CANCELLED).first()
    if existing:
        return existing, False
    gross, allowances, tax_pct = _structure_amounts(emp)
    att = Attendance.objects.filter(tenant=tenant, employee=emp, attendance_date__gte=start, attendance_date__lte=end)
    late_fine = att.aggregate(s=Sum('late_fine'))['s'] or Decimal('0')
    hours = att.aggregate(s=Sum('hours_worked'))['s'] or Decimal('0')
    tax = (gross * tax_pct / Decimal('100')) if tax_pct else Decimal('0')
    deductions = tax + late_fine
    net = gross - deductions
    if net < 0:
        net = Decimal('0')
    n = Payroll.objects.filter(tenant=tenant).count() + 1
    row = Payroll.objects.create(
        tenant=tenant,
        payroll_number=f'PAY-{tenant.id}-{n:05d}',
        employee=emp,
        pay_period_start=start,
        pay_period_end=end,
        pay_date=end,
        base_salary=gross - allowances,
        allowances=allowances,
        hours_worked=hours,
        gross_pay=gross,
        tax=tax,
        other_deductions=late_fine,
        total_deductions=deductions,
        net_pay=net,
        status=PayrollStatus.DRAFT,
        created_by=user,
    )
    return row, True


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payroll(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    _seed(tenant)
    if request.method == 'POST':
        data = request.data or {}
        start = _date(data.get('pay_period_start')) or date.today().replace(day=1)
        end = _date(data.get('pay_period_end')) or date.today()
        emp = _emp(tenant, data.get('employee_id'))
        created = []
        if emp:
            row, _ = _generate_payroll(tenant, emp, start, end, request.user)
            created.append(row)
        else:
            for staff in Employee.objects.filter(tenant=tenant, status=EmploymentStatus.ACTIVE):
                row, is_new = _generate_payroll(tenant, staff, start, end, request.user)
                if is_new:
                    created.append(row)
        items = [serialize_payroll(r) for r in created]
        return Response({'items': items, 'created': len(items)}, status=201)
    qs = Payroll.objects.select_related('employee').filter(tenant=tenant).order_by('-id')
    paid_only = str(request.query_params.get('paid') or '') in ('1', 'true')
    if paid_only:
        qs = qs.filter(status=PayrollStatus.PAID)
    items = [serialize_payroll(r) for r in qs[:400]]
    return Response({
        'items': items,
        'options': _options(tenant),
        'summary': {
            'slips': len(items),
            'net': round(sum(r['net_pay'] for r in items), 2),
        },
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payroll_action(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    try:
        row = Payroll.objects.select_related('employee').get(id=pk, tenant=tenant)
    except Payroll.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    action = (request.data or {}).get('action')
    now = timezone.now()
    try:
        if action == 'approve' and row.status in (PayrollStatus.DRAFT, PayrollStatus.PENDING):
            row.status = PayrollStatus.APPROVED
            row.approved_by = request.user
            row.approved_at = now
            row.save()
            post_payroll_accrual(row, user=request.user)
            row.refresh_from_db()
        elif action == 'pay' and row.status == PayrollStatus.APPROVED:
            row.status = PayrollStatus.PAID
            row.paid_by = request.user
            row.paid_at = now
            row.payment_method = (request.data or {}).get('method') or 'bank'
            row.pay_date = _date((request.data or {}).get('pay_date')) or date.today()
            row.save()
            # Ensure accrual exists (legacy approved slips)
            if not row.accrual_journal_id:
                post_payroll_accrual(row, user=request.user)
                row.refresh_from_db()
            post_payroll_payment(row, user=request.user)
            row.refresh_from_db()
        elif action == 'cancel' and row.status != PayrollStatus.PAID:
            if row.accrual_journal_id:
                reverse_payroll_accrual(row, user=request.user)
                row.refresh_from_db()
            row.status = PayrollStatus.CANCELLED
            row.save(update_fields=['status', 'updated_at'])
        else:
            return Response({'detail': f'Cannot {action} this payroll'}, status=400)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=400)
    except Exception as exc:
        return Response({'detail': str(exc)}, status=400)
    return Response(serialize_payroll(row))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payroll_bulk_pay(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    method = (request.data or {}).get('method') or 'bank'
    qs = Payroll.objects.select_related('employee').filter(tenant=tenant, status=PayrollStatus.APPROVED)
    ids = (request.data or {}).get('ids') or []
    if ids:
        qs = qs.filter(id__in=ids)
    now = timezone.now()
    paid = []
    errors = []
    for row in qs:
        try:
            row.status = PayrollStatus.PAID
            row.paid_by = request.user
            row.paid_at = now
            row.payment_method = method
            row.pay_date = date.today()
            row.save()
            if not row.accrual_journal_id:
                post_payroll_accrual(row, user=request.user)
                row.refresh_from_db()
            post_payroll_payment(row, user=request.user)
            row.refresh_from_db()
            paid.append(serialize_payroll(row))
        except Exception as exc:
            errors.append({'id': row.id, 'payroll_number': row.payroll_number, 'detail': str(exc)})
    return Response({'items': paid, 'paid': len(paid), 'errors': errors})


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def settings_view(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    row = _settings(tenant)
    if request.method != 'GET':
        data = request.data or {}
        row.work_start = (data.get('work_start') or row.work_start).strip()
        row.work_end = (data.get('work_end') or row.work_end).strip()
        if 'late_grace_minutes' in data:
            row.late_grace_minutes = max(0, _int(data.get('late_grace_minutes'), row.late_grace_minutes))
        if 'late_fine_amount' in data:
            row.late_fine_amount = _dec(data.get('late_fine_amount'), str(row.late_fine_amount))
        if 'overtime_rate' in data:
            row.overtime_rate = _dec(data.get('overtime_rate'), str(row.overtime_rate))
        row.save()
    return Response({
        'work_start': row.work_start,
        'work_end': row.work_end,
        'late_grace_minutes': row.late_grace_minutes,
        'late_fine_amount': _money(row.late_fine_amount),
        'overtime_rate': _money(row.overtime_rate),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    _seed(tenant)
    today = timezone.localdate()
    month_start = today.replace(day=1)
    employees = Employee.objects.filter(tenant=tenant, status=EmploymentStatus.ACTIVE)
    present_ids = set(
        Attendance.objects.filter(tenant=tenant, attendance_date=today, check_in__isnull=False).values_list(
            'employee_id', flat=True
        )
    )
    on_leave = HrLeaveRequest.objects.filter(
        tenant=tenant, status='approved', date_from__lte=today, date_to__gte=today
    ).count()
    late_today = Attendance.objects.filter(tenant=tenant, attendance_date=today, late_minutes__gt=0).count()
    pending_leave = HrLeaveRequest.objects.filter(tenant=tenant, status='pending').count()
    pending_loans = HrLoan.objects.filter(tenant=tenant, status='pending').count()
    payroll_month = Payroll.objects.filter(tenant=tenant, pay_period_start__gte=month_start).exclude(
        status=PayrollStatus.CANCELLED
    )
    return Response({
        'cards': [
            {'label': 'Active staff', 'value': employees.count()},
            {'label': 'Present today', 'value': len(present_ids)},
            {'label': 'On leave today', 'value': on_leave},
            {'label': 'Late today', 'value': late_today},
            {'label': 'Pending leave', 'value': pending_leave},
            {'label': 'Pending loans', 'value': pending_loans},
            {'label': 'Payroll slips (month)', 'value': payroll_month.count()},
            {'label': 'Payroll net (month)', 'value': _money(payroll_month.aggregate(s=Sum('net_pay'))['s'])},
        ],
        'today': today.isoformat(),
    })


def _period(request):
    start = _date(request.query_params.get('from')) or date.today().replace(day=1)
    end = _date(request.query_params.get('to')) or date.today()
    if end < start:
        start, end = end, start
    return start, end


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hr_report(request, kind):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied
    tenant = _tenant(request)
    if not tenant:
        return Response({'detail': 'No tenant'}, status=400)
    start, end = _period(request)

    if kind == 'monthly-attendance':
        rows = []
        att = Attendance.objects.select_related('employee').filter(
            tenant=tenant, attendance_date__gte=start, attendance_date__lte=end
        )
        grouped = defaultdict(lambda: {'present': 0, 'hours': 0.0, 'late': 0})
        for rec in att:
            key = rec.employee.full_name
            if rec.check_in:
                grouped[key]['present'] += 1
            grouped[key]['hours'] += float(rec.hours_worked or 0)
            if rec.late_minutes and rec.late_minutes > 0:
                grouped[key]['late'] += 1
        for name, val in sorted(grouped.items()):
            rows.append({
                'employee': name,
                'present_days': val['present'],
                'hours': round(val['hours'], 2),
                'late_days': val['late'],
            })
        return Response({
            'columns': ['Employee', 'Present days', 'Hours', 'Late days'],
            'rows': rows,
            'summary': {'staff': len(rows)},
        })

    if kind == 'late-fine':
        att = Attendance.objects.select_related('employee').filter(
            tenant=tenant, attendance_date__gte=start, attendance_date__lte=end, late_minutes__gt=0
        )
        rows = [
            {
                'date': r.attendance_date.isoformat(),
                'employee': r.employee.full_name,
                'in': r.check_in.strftime('%H:%M') if r.check_in else '',
                'late_minutes': _money(r.late_minutes),
                'fine': _money(r.late_fine),
            }
            for r in att.order_by('attendance_date')
        ]
        return Response({
            'columns': ['Date', 'Employee', 'In', 'Late minutes', 'Fine'],
            'rows': rows,
            'summary': {'incidents': len(rows), 'fine': round(sum(r['fine'] for r in rows), 2)},
        })

    if kind == 'leave':
        qs = HrLeaveRequest.objects.select_related('employee', 'leave_type').filter(
            tenant=tenant, date_from__lte=end, date_to__gte=start
        )
        rows = [
            {
                'employee': r.employee.full_name,
                'type': r.leave_type.name if r.leave_type_id else '',
                'from': r.date_from.isoformat(),
                'to': r.date_to.isoformat(),
                'days': float(r.days or 0),
                'status': r.status,
            }
            for r in qs.order_by('date_from')
        ]
        return Response({
            'columns': ['Employee', 'Type', 'From', 'To', 'Days', 'Status'],
            'rows': rows,
            'summary': {'requests': len(rows), 'days': round(sum(r['days'] for r in rows), 1)},
        })

    if kind == 'payroll':
        qs = Payroll.objects.select_related('employee').filter(
            tenant=tenant, pay_period_start__lte=end, pay_period_end__gte=start
        ).exclude(status=PayrollStatus.CANCELLED)
        rows = [
            {
                'number': r.payroll_number,
                'employee': r.employee.full_name,
                'period': f'{r.pay_period_start} → {r.pay_period_end}',
                'gross': _money(r.gross_pay),
                'deductions': _money(r.total_deductions),
                'net': _money(r.net_pay),
                'status': r.status,
            }
            for r in qs.order_by('pay_period_start')
        ]
        return Response({
            'columns': ['Payroll', 'Employee', 'Period', 'Gross', 'Deductions', 'Net', 'Status'],
            'rows': rows,
            'summary': {'slips': len(rows), 'net': round(sum(r['net'] for r in rows), 2)},
        })

    if kind == 'salary-payment':
        qs = Payroll.objects.select_related('employee').filter(
            tenant=tenant, status=PayrollStatus.PAID, pay_date__gte=start, pay_date__lte=end
        )
        rows = [
            {
                'date': r.pay_date.isoformat() if r.pay_date else '',
                'number': r.payroll_number,
                'employee': r.employee.full_name,
                'method': r.payment_method or '',
                'net': _money(r.net_pay),
            }
            for r in qs.order_by('pay_date')
        ]
        return Response({
            'columns': ['Date', 'Payroll', 'Employee', 'Method', 'Net'],
            'rows': rows,
            'summary': {'payments': len(rows), 'amount': round(sum(r['net'] for r in rows), 2)},
        })

    return Response({'detail': f'Unknown report: {kind}'}, status=400)
