"""Amortization schedule helpers (FSERP loan_schedule port)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from dateutil.relativedelta import relativedelta


TWOPLACES = Decimal('0.01')


def _q(v) -> Decimal:
    return Decimal(str(v or 0)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def amortized_schedule(
    principal: Decimal,
    annual_rate_pct: Decimal,
    term_months: int,
    start_date: Optional[date] = None,
) -> List[dict]:
    """Reducing-balance EMI schedule. Returns list of installment dicts."""
    principal = _q(principal)
    rate = Decimal(str(annual_rate_pct or 0))
    months = int(term_months or 0)
    if principal <= 0 or months <= 0:
        return []

    start = start_date or date.today()
    monthly_rate = (rate / Decimal('100')) / Decimal('12') if rate else Decimal('0')

    if monthly_rate > 0:
        factor = (Decimal('1') + monthly_rate) ** months
        emi = _q(principal * monthly_rate * factor / (factor - Decimal('1')))
    else:
        emi = _q(principal / Decimal(months))

    balance = principal
    rows: List[dict] = []
    for i in range(1, months + 1):
        interest = _q(balance * monthly_rate) if monthly_rate else Decimal('0')
        if i == months:
            principal_part = balance
            payment = _q(principal_part + interest)
        else:
            principal_part = _q(emi - interest)
            if principal_part > balance:
                principal_part = balance
            payment = _q(principal_part + interest)
        balance = _q(balance - principal_part)
        due = start + relativedelta(months=i)
        rows.append({
            'installment': i,
            'due_date': due.isoformat(),
            'payment': float(payment),
            'principal': float(principal_part),
            'interest': float(interest),
            'balance': float(max(balance, Decimal('0'))),
        })
    return rows
