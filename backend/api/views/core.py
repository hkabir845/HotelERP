"""Core endpoints: health check and root."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'version': '1.0.0',
        'framework': 'Django',
        'application': 'Hotel & Resort Management ERP',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def root(request):
    """Root endpoint."""
    return Response({
        'message': 'Hotel & Resort Management ERP API - Multi-Tenant SaaS',
        'docs': '/api/docs',
        'health': '/api/core/health/',
        'version': getattr(settings, 'APP_VERSION', '1.0.0'),
    })
