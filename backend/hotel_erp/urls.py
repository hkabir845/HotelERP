"""
URL configuration for Hotel ERP project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]

# Serve uploads via gunicorn (Cloudflare → nginx → API).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
