"""
URL configuration for syntra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from accounts.views import dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── API routes ──
    path('api/auth/', include('accounts.api_urls')),
    path('api/organizer/', include('organizer.api_urls')),
    path('api/participant/', include('participant.api_urls')),

    # ── Template-based routes ──
    path('accounts/', include('accounts.urls')),
    path('organizer/', include('organizer.urls')),
    path('participant/', include('participant.urls')),

    # Authenticated dashboard (after login)
    path('dashboard/', dashboard_view, name='dashboard'),

    # Public landing page (unauthenticated users see this)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
