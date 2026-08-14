"""Return JSON for unhandled API errors instead of Django's HTML 500 page."""
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response

    logger.exception('Unhandled API error')
    detail = str(exc) if settings.DEBUG else 'Internal server error'
    return Response({'detail': detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
