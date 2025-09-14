# lumos_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from user_management.urls import user_urlpatterns
from notes.urls import notes_url_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/v1/users/", include(user_urlpatterns)),
    path("api/v1/", include(notes_url_patterns)),
    # JWT token endpoints
    path(
        "api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/v1/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Health check endpoint
    path("health/", lambda request: HttpResponse("OK")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Import HttpResponse for health check
from django.http import HttpResponse
