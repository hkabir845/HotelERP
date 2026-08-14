"""Check-in, check-out, cancel, and guest folio."""
from datetime import date
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.models import (
    Bill,
    BillItem,
    BillPayment,
    BillStatus,
    BillType,
    HousekeepingTask,
    PaymentMethod,
    Reservation,
    ReservationStatus,
    Room,
    RoomStatusEnum,
    TaskPriority,
    TaskType,
)
from api.services.hotel_gl import post_folio_charge, post_folio_payment
from api.views import deny_if_no_tenant
from django.db import transaction


def _tenant(request):
    return getattr(request.user, 'tenant', None)


def _get_reservation(request, pk):
    denied = deny_if_no_tenant(request.user)
    if denied:
        return None, denied
    tenant = _tenant(request)
    qs = Reservation.objects.select_related('guest', 'room', 'room__room_type')
    if tenant:
        qs = qs.filter(tenant=tenant)
    try:
        return qs.get(pk=pk), None
    except Reservation.DoesNotExist:
        return None, Response({'detail': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)


def _serialize_reservation(res):
    nights = 0
    if res.check_in_date and res.check_out_date:
        nights = max(0, (res.check_out_date - res.check_in_date).days)
    return {
        'id': res.id,
        'reservation_number': res.reservation_number,
        'guest': {
            'id': res.guest_id,
            'name': f'{res.guest.first_name} {res.guest.last_name}' if res.guest_id else '',
            'email': res.guest.email if res.guest_id else None,
            'phone': res.guest.phone if res.guest_id else None,
            'is_vip': res.guest.is_vip if res.guest_id else False,
        },
        'room': {
            'id': res.room.id,
            'room_number': res.room.room_number,
            'room_type': res.room.room_type.name,
        } if res.room_id else None,
        'check_in_date': res.check_in_date.isoformat() if res.check_in_date else None,
        'check_out_date': res.check_out_date.isoformat() if res.check_out_date else None,
        'actual_check_in': res.actual_check_in.isoformat() if res.actual_check_in else None,
        'actual_check_out': res.actual_check_out.isoformat() if res.actual_check_out else None,
        'status': res.status,
        'reservation_type': res.reservation_type,
        'adults': res.adults,
        'children': res.children,
        'room_rate': float(res.room_rate or 0),
        'total_amount': float(res.total_amount or 0),
        'paid_amount': float(res.paid_amount or 0),
        'balance': float(res.balance or 0),
        'source': res.source,
        'notes': res.notes or '',
        'nights': nights,
    }


def _get_or_create_folio(res):
    bill = Bill.objects.filter(reservation=res).order_by('id').first()
    if bill:
        return bill
    return Bill.objects.create(
        tenant=res.tenant,
        bill_number=f'FOL-{res.tenant_id}-{res.id}',
        guest=res.guest,
        reservation=res,
        room=res.room,
        bill_type=BillType.CONSOLIDATED,
        bill_date=date.today(),
        subtotal=0,
        total_amount=0,
        paid_amount=0,
        balance=0,
        status=BillStatus.PENDING,
        notes=f'Folio for {res.reservation_number}',
    )


def _recalc(res, bill):
    charges = sum((item.line_total or 0) for item in bill.items.all())
    pays = sum((pay.amount or 0) for pay in bill.payments.all())
    charges = Decimal(str(charges))
    pays = Decimal(str(pays))
    bill.subtotal = charges
    bill.total_amount = charges
    bill.paid_amount = pays
    bill.balance = charges - pays
    if pays <= 0:
        bill.status = BillStatus.PENDING
    elif bill.balance <= 0:
        bill.status = BillStatus.PAID
    else:
        bill.status = BillStatus.PARTIAL
    bill.save()
    res.total_amount = charges if charges else res.total_amount
    res.paid_amount = pays
    res.balance = (charges if charges else Decimal(str(res.total_amount or 0))) - pays
    res.save(update_fields=['total_amount', 'paid_amount', 'balance', 'updated_at'])
    return bill


def _ensure_room_charge(res, bill, user=None):
    if bill.items.exists():
        return
    nights = 1
    if res.check_in_date and res.check_out_date:
        nights = max(1, (res.check_out_date - res.check_in_date).days)
    unit = Decimal(str(res.room_rate or 0))
    line_total = Decimal(str(res.total_amount or 0)) or (unit * nights)
    room_label = res.room.room_number if res.room_id else 'unassigned'
    item = BillItem.objects.create(
        bill=bill,
        description=f'Room rent {room_label} × {nights} night(s)',
        item_type='room_charge',
        quantity=nights,
        unit_price=unit or line_total,
        line_total=line_total,
        charge_date=timezone.now(),
    )
    try:
        post_folio_charge(res.tenant, item, user=user, reservation_number=res.reservation_number)
    except Exception:
        # Folio must still open even if COA not seeded yet
        pass
    if Decimal(str(res.paid_amount or 0)) > 0 and not bill.payments.exists():
        pay = BillPayment.objects.create(
            bill=bill,
            payment_number=f'OPN-{res.tenant_id}-{res.id}',
            payment_date=timezone.now(),
            amount=Decimal(str(res.paid_amount)),
            payment_method=PaymentMethod.CASH,
            amount_in_base_currency=Decimal(str(res.paid_amount)),
            notes='Opening payment from reservation',
        )
        try:
            post_folio_payment(res.tenant, pay, user=user, reservation_number=res.reservation_number)
        except Exception:
            pass


def _folio_payload(res, user=None):
    bill = _get_or_create_folio(res)
    _ensure_room_charge(res, bill, user=user)
    _recalc(res, bill)
    bill.refresh_from_db()
    res.refresh_from_db()
    charges = [
        {
            'id': item.id,
            'description': item.description,
            'quantity': float(item.quantity or 1),
            'unit_price': float(item.unit_price or 0),
            'amount': float(item.line_total or 0),
            'type': item.item_type or 'charge',
        }
        for item in bill.items.all().order_by('id')
    ]
    payments = [
        {
            'id': pay.id,
            'description': pay.notes or pay.payment_method,
            'method': pay.payment_method,
            'amount': float(pay.amount or 0),
            'date': pay.payment_date.isoformat() if pay.payment_date else None,
        }
        for pay in bill.payments.all().order_by('id')
    ]
    return {
        'reservation': _serialize_reservation(res),
        'folio': {
            'bill_number': bill.bill_number,
            'status': bill.status,
            'charges': charges,
            'payments': payments,
            'total_amount': float(bill.total_amount or 0),
            'paid_amount': float(bill.paid_amount or 0),
            'balance': float(bill.balance or 0),
        },
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reservation_detail(request, pk):
    res, err = _get_reservation(request, pk)
    if err:
        return err
    return Response(_folio_payload(res, user=request.user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in(request, pk):
    res, err = _get_reservation(request, pk)
    if err:
        return err
    if res.status in (ReservationStatus.CHECKED_OUT, ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW):
        return Response({'detail': f'Cannot check in a {res.status} reservation'}, status=status.HTTP_400_BAD_REQUEST)
    if res.status == ReservationStatus.CHECKED_IN:
        return Response(_folio_payload(res, user=request.user))
    room_id = request.data.get('room_id') if isinstance(request.data, dict) else None
    if room_id and not res.room_id:
        try:
            room = Room.objects.get(id=room_id, tenant=res.tenant)
        except Room.DoesNotExist:
            return Response({'detail': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        res.room = room
    if not res.room_id:
        return Response({'detail': 'Assign a room before check-in'}, status=status.HTTP_400_BAD_REQUEST)
    res.status = ReservationStatus.CHECKED_IN
    res.actual_check_in = timezone.now()
    res.save(update_fields=['status', 'actual_check_in', 'room', 'updated_at'])
    Room.objects.filter(id=res.room_id).update(status=RoomStatusEnum.OCCUPIED)
    bill = _get_or_create_folio(res)
    _ensure_room_charge(res, bill)
    _recalc(res, bill)
    from api.services.audit import write_audit
    write_audit(res.tenant, request.user, 'check_in', 'reservation', res.id, res.reservation_number, res.room.room_number if res.room_id else '')
    return Response(_folio_payload(res, user=request.user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_out(request, pk):
    res, err = _get_reservation(request, pk)
    if err:
        return err
    if res.status != ReservationStatus.CHECKED_IN:
        return Response({'detail': 'Only in-house guests can be checked out'}, status=status.HTTP_400_BAD_REQUEST)
    force = bool((request.data or {}).get('force'))
    bill = _get_or_create_folio(res)
    _recalc(res, bill)
    res.refresh_from_db()
    if res.balance > 0 and not force:
        return Response(
            {
                'detail': f'Outstanding balance ${float(res.balance):.2f}. Collect payment or checkout with force=true.',
                'balance': float(res.balance),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    res.status = ReservationStatus.CHECKED_OUT
    res.actual_check_out = timezone.now()
    res.save(update_fields=['status', 'actual_check_out', 'updated_at'])
    from api.services.audit import write_audit
    write_audit(res.tenant, request.user, 'check_out', 'reservation', res.id, res.reservation_number, f'balance {float(res.balance or 0):.2f}')
    if res.room_id:
        Room.objects.filter(id=res.room_id).update(status=RoomStatusEnum.CLEANING)
        HousekeepingTask.objects.create(
            tenant=res.tenant,
            room=res.room,
            task_type=TaskType.CLEANING,
            priority=TaskPriority.HIGH,
            scheduled_date=timezone.now(),
            description=f'Departure clean after {res.reservation_number}',
            assigned_by=request.user,
        )
    return Response(_folio_payload(res, user=request.user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_reservation(request, pk):
    res, err = _get_reservation(request, pk)
    if err:
        return err
    if res.status in (ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT):
        return Response({'detail': 'Check out first, or use no-show only before arrival'}, status=status.HTTP_400_BAD_REQUEST)
    mark = (request.data or {}).get('status') or ReservationStatus.CANCELLED
    if mark not in (ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW):
        mark = ReservationStatus.CANCELLED
    res.status = mark
    res.save(update_fields=['status', 'updated_at'])
    from api.services.audit import write_audit
    write_audit(res.tenant, request.user, mark, 'reservation', res.id, res.reservation_number, (request.data or {}).get('notes') or '')
    if res.room_id:
        Room.objects.filter(id=res.room_id).update(status=RoomStatusEnum.AVAILABLE)
    return Response(_folio_payload(res, user=request.user))


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def folio(request, pk):
    res, err = _get_reservation(request, pk)
    if err:
        return err
    if request.method == 'GET':
        return Response(_folio_payload(res, user=request.user))
    data = request.data or {}
    action = (data.get('action') or 'charge').strip().lower()
    amount = Decimal(str(data.get('amount') or 0))
    if amount <= 0:
        return Response({'detail': 'amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    bill = _get_or_create_folio(res)
    _ensure_room_charge(res, bill, user=request.user)
    if action == 'payment':
        method = data.get('payment_method') or PaymentMethod.CASH
        if method not in PaymentMethod.values:
            method = PaymentMethod.CASH
        n = BillPayment.objects.filter(bill=bill).count() + 1
        try:
            with transaction.atomic():
                pay = BillPayment.objects.create(
                    bill=bill,
                    payment_number=f'PAY-{res.tenant_id}-{res.id}-{n:04d}',
                    payment_date=timezone.now(),
                    amount=amount,
                    payment_method=method,
                    amount_in_base_currency=amount,
                    notes=data.get('description') or data.get('notes') or method,
                    created_by=request.user,
                )
                post_folio_payment(
                    res.tenant, pay, user=request.user, reservation_number=res.reservation_number
                )
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        from api.services.audit import write_audit
        write_audit(res.tenant, request.user, 'folio_payment', 'folio', res.id, res.reservation_number, f'{method} {amount}')
    else:
        qty = Decimal(str(data.get('quantity') or 1))
        try:
            with transaction.atomic():
                item = BillItem.objects.create(
                    bill=bill,
                    description=(data.get('description') or 'Extra charge').strip(),
                    item_type=data.get('item_type') or 'extra',
                    quantity=qty,
                    unit_price=amount,
                    line_total=amount * qty,
                    charge_date=timezone.now(),
                    notes=data.get('notes') or '',
                )
                post_folio_charge(
                    res.tenant, item, user=request.user, reservation_number=res.reservation_number
                )
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        from api.services.audit import write_audit
        write_audit(res.tenant, request.user, 'folio_charge', 'folio', res.id, res.reservation_number, data.get('description') or 'Extra charge')
    return Response(_folio_payload(res, user=request.user), status=status.HTTP_201_CREATED)
