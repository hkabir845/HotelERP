"""
Superadmin SaaS Dashboard endpoints.
⚠️ CRITICAL: DO NOT MODIFY LOGIN ENDPOINT - This is separate from auth!
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import get_db
from app.models import *
from app.models.user import User
from app.models.tenant import Tenant
from app.models.reservation import Reservation, ReservationStatus
from app.models.room import Room
from app.models.guest import Guest
from app.models.billing import Bill, BillStatus
from app.models.employee import Employee
from app.models.work_order import WorkOrder
from app.routers.auth import get_current_user

router = APIRouter(prefix="/superadmin", tags=["Superadmin"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get superadmin SaaS dashboard statistics.
    Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access this endpoint"
        )
    
    # Get all tenants
    total_tenants = db.query(Tenant).count()
    active_tenants = db.query(Tenant).filter(Tenant.is_active == True).count()
    
    # Get total users across all tenants
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Get statistics per tenant
    tenant_stats = []
    tenants = db.query(Tenant).all()
    
    for tenant in tenants:
        # Reservations
        total_reservations = db.query(Reservation).filter(
            Reservation.tenant_id == tenant.id
        ).count()
        
        active_reservations = db.query(Reservation).filter(
            and_(
                Reservation.tenant_id == tenant.id,
                Reservation.status.in_([ReservationStatus.CHECKED_IN, ReservationStatus.CONFIRMED])
            )
        ).count()
        
        # Rooms
        total_rooms = db.query(Room).filter(Room.tenant_id == tenant.id).count()
        occupied_rooms = db.query(Room).filter(
            and_(
                Room.tenant_id == tenant.id,
                Room.status == "occupied"
            )
        ).count()
        
        # Guests
        total_guests = db.query(Guest).filter(Guest.tenant_id == tenant.id).count()
        
        # Revenue (from bills)
        revenue = db.query(func.sum(Bill.total_amount)).filter(
            and_(
                Bill.tenant_id == tenant.id,
                Bill.status == BillStatus.PAID
            )
        ).scalar() or Decimal(0)
        
        # Employees
        total_employees = db.query(Employee).filter(Employee.tenant_id == tenant.id).count()
        
        # Work Orders
        pending_work_orders = db.query(WorkOrder).filter(
            and_(
                WorkOrder.tenant_id == tenant.id,
                WorkOrder.status.in_(["pending", "in_progress"])
            )
        ).count()
        
        tenant_stats.append({
            "tenant_id": tenant.id,
            "tenant_name": tenant.name,
            "subdomain": tenant.subdomain,
            "is_active": tenant.is_active,
            "subscription_plan": tenant.subscription_plan,
            "statistics": {
                "reservations": {
                    "total": total_reservations,
                    "active": active_reservations
                },
                "rooms": {
                    "total": total_rooms,
                    "occupied": occupied_rooms,
                    "occupancy_rate": round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2)
                },
                "guests": {
                    "total": total_guests
                },
                "revenue": {
                    "total": float(revenue)
                },
                "employees": {
                    "total": total_employees
                },
                "work_orders": {
                    "pending": pending_work_orders
                }
            }
        })
    
    # Overall statistics
    total_revenue = db.query(func.sum(Bill.total_amount)).filter(
        Bill.status == BillStatus.PAID
    ).scalar() or Decimal(0)
    
    total_reservations_all = db.query(Reservation).count()
    total_rooms_all = db.query(Room).count()
    total_guests_all = db.query(Guest).count()
    
    return {
        "overview": {
            "tenants": {
                "total": total_tenants,
                "active": active_tenants
            },
            "users": {
                "total": total_users,
                "active": active_users
            },
            "reservations": {
                "total": total_reservations_all
            },
            "rooms": {
                "total": total_rooms_all
            },
            "guests": {
                "total": total_guests_all
            },
            "revenue": {
                "total": float(total_revenue)
            }
        },
        "tenants": tenant_stats
    }


@router.get("/tenants")
async def get_all_tenants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all tenants (superadmin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access this endpoint"
        )
    
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    total = db.query(Tenant).count()
    
    return {
        "total": total,
        "tenants": [
            {
                "id": t.id,
                "name": t.name,
                "subdomain": t.subdomain,
                "domain": t.domain,
                "email": t.email,
                "is_active": t.is_active,
                "subscription_plan": t.subscription_plan,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tenants
        ]
    }


@router.get("/revenue")
async def get_revenue_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get revenue statistics (superadmin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access this endpoint"
        )
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Revenue by tenant
    revenue_by_tenant = db.query(
        Tenant.name,
        Tenant.subdomain,
        func.sum(Bill.total_amount).label("revenue")
    ).join(
        Bill, Bill.tenant_id == Tenant.id
    ).filter(
        and_(
            Bill.status == BillStatus.PAID,
            Bill.bill_date >= start_date.date()
        )
    ).group_by(Tenant.id, Tenant.name, Tenant.subdomain).all()
    
    # Total revenue
    total_revenue = db.query(func.sum(Bill.total_amount)).filter(
        and_(
            Bill.status == BillStatus.PAID,
            Bill.bill_date >= start_date.date()
        )
    ).scalar() or Decimal(0)
    
    return {
        "period_days": days,
        "total_revenue": float(total_revenue),
        "revenue_by_tenant": [
            {
                "tenant_name": r.name,
                "subdomain": r.subdomain,
                "revenue": float(r.revenue or 0)
            }
            for r in revenue_by_tenant
        ]
    }

