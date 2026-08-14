"""Islamic financing terminology (FSERP loan_islamic port)."""
from __future__ import annotations

from api.models import Loan

ISLAMIC_CONTRACT_VARIANTS = [
    ('', 'General Islamic financing'),
    ('murabaha', 'Murabaha'),
    ('ijara', 'Ijara'),
    ('musharaka', 'Musharaka'),
    ('mudaraba', 'Mudaraba'),
    ('bai_muajjal', 'Bai Muajjal'),
    ('istisna', 'Istisna'),
]


def loan_uses_islamic_terminology(lo: Loan) -> bool:
    bm = (lo.banking_model or Loan.BANKING_CONVENTIONAL).strip().lower()
    if bm == Loan.BANKING_ISLAMIC:
        return True
    pt = lo.product_type or Loan.PRODUCT_GENERAL
    return pt in (Loan.PRODUCT_ISLAMIC_FACILITY, Loan.PRODUCT_ISLAMIC_DEAL)


def charge_label(lo: Loan) -> str:
    """UI label for the cost of funds."""
    if loan_uses_islamic_terminology(lo):
        return 'Profit'
    if not getattr(lo, 'interest_bearing', True):
        return 'Interest-free'
    return 'Interest'
