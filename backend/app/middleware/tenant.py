"""
Multi-tenant middleware for domain-based tenant routing.
"""
from typing import Optional
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant import Tenant
from app.config import settings


def get_tenant_from_domain(domain: str, db: Session) -> Optional[Tenant]:
    """
    Get tenant from domain or subdomain.
    
    Args:
        domain: Domain or subdomain (e.g., 'turag.pms.com' or 'turag')
        db: Database session
    
    Returns:
        Tenant object or None
    """
    # Try exact domain match first
    tenant = db.query(Tenant).filter(
        (Tenant.domain == domain) | (Tenant.subdomain == domain)
    ).first()
    
    if tenant and tenant.is_active:
        return tenant
    
    return None


def get_current_tenant(request: Request, db: Optional[Session] = None) -> Optional[Tenant]:
    """
    Get current tenant from request.
    
    Checks in order:
    1. X-Tenant-ID header
    2. X-Tenant-Subdomain header
    3. Host header (domain/subdomain)
    
    Args:
        request: FastAPI request object
        db: Optional database session (will create one if not provided)
    
    Returns:
        Tenant object or None
    """
    # Get database session
    should_close = False
    if db is None:
        db = next(get_db())
        should_close = True
    
    try:
        # Check X-Tenant-ID header
        tenant_id = request.headers.get(settings.TENANT_ID_HEADER)
        if tenant_id:
            try:
                tenant = db.query(Tenant).filter(
                    Tenant.id == int(tenant_id),
                    Tenant.is_active == True
                ).first()
                if tenant:
                    return tenant
            except (ValueError, TypeError):
                pass
        
        # Check X-Tenant-Subdomain header
        tenant_subdomain = request.headers.get(settings.TENANT_HEADER)
        if tenant_subdomain:
            tenant = get_tenant_from_domain(tenant_subdomain, db)
            if tenant:
                return tenant
        
        # Check Host header
        host = request.headers.get("host", "")
        if host:
            # Remove port if present
            domain = host.split(":")[0]
            # Try full domain
            tenant = get_tenant_from_domain(domain, db)
            if tenant:
                return tenant
            # Try subdomain (first part before dot)
            if "." in domain:
                subdomain = domain.split(".")[0]
                tenant = get_tenant_from_domain(subdomain, db)
                if tenant:
                    return tenant
        
        return None
    
    finally:
        if should_close:
            db.close()


async def tenant_middleware(request: Request, call_next):
    """
    Multi-tenant middleware.
    
    Attaches tenant to request.state for use in routes.
    """
    tenant = get_current_tenant(request)
    request.state.tenant = tenant
    
    response = await call_next(request)
    return response

