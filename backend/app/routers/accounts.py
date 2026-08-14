"""
Accounts router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime
from decimal import Decimal
import uuid

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/chart-of-accounts")
async def get_chart_of_accounts(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chart of accounts."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock hierarchical data
    accounts = [
        {
            "id": 1,
            "code": "1000",
            "name": "Assets",
            "account_type": "asset",
            "parent_id": None,
            "balance": 0,
            "is_group": True,
            "level": 0,
            "children": [
                {
                    "id": 2,
                    "code": "1100",
                    "name": "Current Assets",
                    "account_type": "asset",
                    "parent_id": 1,
                    "balance": 0,
                    "is_group": True,
                    "level": 1,
                    "children": [
                        {
                            "id": 3,
                            "code": "1110",
                            "name": "Cash",
                            "account_type": "asset",
                            "parent_id": 2,
                            "balance": 50000.00,
                            "is_group": False,
                            "level": 2
                        },
                        {
                            "id": 4,
                            "code": "1120",
                            "name": "Bank",
                            "account_type": "asset",
                            "parent_id": 2,
                            "balance": 150000.00,
                            "is_group": False,
                            "level": 2
                        }
                    ]
                }
            ]
        },
        {
            "id": 5,
            "code": "2000",
            "name": "Liabilities",
            "account_type": "liability",
            "parent_id": None,
            "balance": 0,
            "is_group": True,
            "level": 0,
            "children": [
                {
                    "id": 6,
                    "code": "2100",
                    "name": "Accounts Payable",
                    "account_type": "liability",
                    "parent_id": 5,
                    "balance": 25000.00,
                    "is_group": False,
                    "level": 1
                }
            ]
        },
        {
            "id": 7,
            "code": "4000",
            "name": "Revenue",
            "account_type": "revenue",
            "parent_id": None,
            "balance": 0,
            "is_group": True,
            "level": 0,
            "children": [
                {
                    "id": 8,
                    "code": "4100",
                    "name": "Room Revenue",
                    "account_type": "revenue",
                    "parent_id": 7,
                    "balance": 500000.00,
                    "is_group": False,
                    "level": 1
                },
                {
                    "id": 9,
                    "code": "4200",
                    "name": "F&B Revenue",
                    "account_type": "revenue",
                    "parent_id": 7,
                    "balance": 150000.00,
                    "is_group": False,
                    "level": 1
                }
            ]
        },
        {
            "id": 10,
            "code": "5000",
            "name": "Expenses",
            "account_type": "expense",
            "parent_id": None,
            "balance": 0,
            "is_group": True,
            "level": 0,
            "children": [
                {
                    "id": 11,
                    "code": "5100",
                    "name": "Salaries",
                    "account_type": "expense",
                    "parent_id": 10,
                    "balance": -80000.00,
                    "is_group": False,
                    "level": 1
                },
                {
                    "id": 12,
                    "code": "5200",
                    "name": "Utilities",
                    "account_type": "expense",
                    "parent_id": 10,
                    "balance": -15000.00,
                    "is_group": False,
                    "level": 1
                }
            ]
        }
    ]
    
    # Flatten for search
    def flatten_accounts(acc_list, result=None):
        if result is None:
            result = []
        for acc in acc_list:
            result.append(acc)
            if acc.get('children'):
                flatten_accounts(acc['children'], result)
        return result
    
    if search:
        all_accounts = flatten_accounts(accounts)
        filtered_accounts = [a for a in all_accounts if 
                            search.lower() in a['code'].lower() or
                            search.lower() in a['name'].lower()]
        # Rebuild hierarchy with filtered accounts
        # For simplicity, return flat list when searching
        return {"accounts": filtered_accounts}
    
    return {"accounts": accounts}


@router.get("/vouchers")
async def get_vouchers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accounting vouchers."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    vouchers = [
        {
            "id": 1,
            "voucher_number": f"VCH-2024-{str(uuid.uuid4())[:8].upper()}",
            "voucher_type": "cash_payment",
            "date": datetime.now().isoformat(),
            "amount": 5000.00,
            "description": "Payment to supplier",
            "status": "posted",
            "created_by": current_user.first_name + " " + current_user.last_name
        },
        {
            "id": 2,
            "voucher_number": f"VCH-2024-{str(uuid.uuid4())[:8].upper()}",
            "voucher_type": "cash_receipt",
            "date": datetime.now().isoformat(),
            "amount": 12000.00,
            "description": "Guest payment",
            "status": "posted",
            "created_by": current_user.first_name + " " + current_user.last_name
        },
        {
            "id": 3,
            "voucher_number": f"VCH-2024-{str(uuid.uuid4())[:8].upper()}",
            "voucher_type": "bank_payment",
            "date": datetime.now().isoformat(),
            "amount": 3000.00,
            "description": "Utility bill payment",
            "status": "draft",
            "created_by": current_user.first_name + " " + current_user.last_name
        }
    ]
    
    filtered = vouchers
    if type and type != 'all':
        filtered = [v for v in filtered if v['voucher_type'] == type]
    if search:
        filtered = [v for v in filtered if search.lower() in v['voucher_number'].lower() or
                   (v.get('description') and search.lower() in v['description'].lower())]
    
    total = len(filtered)
    total_pages = (total + limit - 1) // limit
    paginated = filtered[(page - 1) * limit:page * limit]
    
    return {
        "vouchers": paginated,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/payable")
async def get_payables(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accounts payable."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    payables = [
        {
            "id": 1,
            "invoice_number": f"INV-{str(uuid.uuid4())[:8].upper()}",
            "vendor_name": "Supplier ABC",
            "vendor_id": 1,
            "invoice_date": datetime.now().isoformat(),
            "due_date": (datetime.now().replace(day=datetime.now().day + 15)).isoformat(),
            "total_amount": 5000.00,
            "paid_amount": 0.00,
            "balance": 5000.00,
            "status": "pending",
            "days_overdue": 0
        },
        {
            "id": 2,
            "invoice_number": f"INV-{str(uuid.uuid4())[:8].upper()}",
            "vendor_name": "Vendor XYZ",
            "vendor_id": 2,
            "invoice_date": (datetime.now().replace(day=datetime.now().day - 5)).isoformat(),
            "due_date": (datetime.now().replace(day=datetime.now().day - 2)).isoformat(),
            "total_amount": 3000.00,
            "paid_amount": 1000.00,
            "balance": 2000.00,
            "status": "overdue",
            "days_overdue": 2
        }
    ]
    
    filtered = payables
    if status and status != 'all':
        filtered = [p for p in filtered if p['status'] == status]
    if search:
        filtered = [p for p in filtered if search.lower() in p['invoice_number'].lower() or
                   search.lower() in p['vendor_name'].lower()]
    
    return {"payables": filtered}


@router.get("/receivable")
async def get_receivables(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accounts receivable."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    receivables = [
        {
            "id": 1,
            "invoice_number": f"INV-{str(uuid.uuid4())[:8].upper()}",
            "customer_name": "Corporate Client A",
            "customer_id": 1,
            "invoice_date": datetime.now().isoformat(),
            "due_date": (datetime.now().replace(day=datetime.now().day + 30)).isoformat(),
            "total_amount": 10000.00,
            "paid_amount": 0.00,
            "balance": 10000.00,
            "status": "pending",
            "days_overdue": 0
        },
        {
            "id": 2,
            "invoice_number": f"INV-{str(uuid.uuid4())[:8].upper()}",
            "customer_name": "Company B",
            "customer_id": 2,
            "invoice_date": (datetime.now().replace(day=datetime.now().day - 10)).isoformat(),
            "due_date": (datetime.now().replace(day=datetime.now().day - 3)).isoformat(),
            "total_amount": 7500.00,
            "paid_amount": 2500.00,
            "balance": 5000.00,
            "status": "overdue",
            "days_overdue": 3
        }
    ]
    
    filtered = receivables
    if status and status != 'all':
        filtered = [r for r in filtered if r['status'] == status]
    if search:
        filtered = [r for r in filtered if search.lower() in r['invoice_number'].lower() or
                   search.lower() in r['customer_name'].lower()]
    
    return {"receivables": filtered}
