"""
FastAPI Backend for Hotel & Resort Management ERP System
World-Class Multi-Tenant SaaS Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

# Import middleware
from app.middleware.tenant import tenant_middleware
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware
from app.config import settings

# Import routers
from app.routers import auth, superadmin, housekeeping, frontdesk, reservations, fnb, accounts, inventory, assets, utilities, broadcast
# from app.routers import reports

app = FastAPI(
    title="Hotel & Resort Management ERP API",
    description="World-Class Professional Hotel & Resort Management System - Multi-Tenant SaaS",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Frontdesk", "description": "Reservations, Check-in/out, Guest Management"},
        {"name": "Housekeeping", "description": "Room Status, Task Management"},
        {"name": "F&B", "description": "Food & Beverage, Menu, Orders, Recipe Management"},
        {"name": "Accounting", "description": "Full Accounting System (GL, AP, AR, Reports)"},
        {"name": "Asset & Maintenance", "description": "Asset Management, Maintenance"},
        {"name": "Broadcast", "description": "System-wide messaging"},
        {"name": "Utilities", "description": "Settings, User Management"},
        {"name": "Reports", "description": "Comprehensive reporting"},
        {"name": "Superadmin", "description": "Multi-tenant management"},
    ]
)

# Security Headers Middleware (first)
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# CORS Configuration - Must be added before tenant middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With", settings.TENANT_HEADER, settings.TENANT_ID_HEADER],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,
)

# Tenant Middleware (last, so it can access all request data)
@app.middleware("http")
async def tenant_middleware_wrapper(request, call_next):
    return await tenant_middleware(request, call_next)

# Health check endpoint
@app.get("/api/core/health/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "framework": "FastAPI",
        "application": "Hotel & Resort Management ERP"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hotel & Resort Management ERP API - Multi-Tenant SaaS",
        "docs": "/api/docs",
        "health": "/api/core/health/",
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(superadmin.router, prefix="/api", tags=["Superadmin"])
app.include_router(housekeeping.router, prefix="/api", tags=["Housekeeping"])
app.include_router(frontdesk.router, prefix="/api", tags=["Frontdesk"])
app.include_router(reservations.router, prefix="/api", tags=["Reservations"])
app.include_router(fnb.router, prefix="/api", tags=["F&B"])
app.include_router(accounts.router, prefix="/api", tags=["Accounts"])
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(assets.router, prefix="/api", tags=["Assets & Maintenance"])
app.include_router(utilities.router, prefix="/api", tags=["Utilities"])
app.include_router(broadcast.router, prefix="/api", tags=["Broadcast"])

# Note: Additional routers can be added here as modules are implemented
# app.include_router(reports.router, prefix="/api", tags=["Reports"])
# app.include_router(fnb.router, prefix="/api/fnb", tags=["F&B"])
# app.include_router(accounting.router, prefix="/api/accounting", tags=["Accounting"])
# app.include_router(asset.router, prefix="/api/asset", tags=["Asset & Maintenance"])
# app.include_router(broadcast.router, prefix="/api/broadcast", tags=["Broadcast"])
# app.include_router(utilities.router, prefix="/api/utilities", tags=["Utilities"])
# app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

if __name__ == "__main__":
    import sys
    import os
    # Add parent directory to path so app can be imported
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

