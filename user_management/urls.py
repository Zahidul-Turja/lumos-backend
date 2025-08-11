from django.urls import path
from user_management.views import (
    request_magic_link,
    verify_magic_link,
    google_auth,
    logout,
    UserProfileView,
    user_sessions,
)

user_urlpatterns = [
    # Authentication endpoints
    path("auth/magic-link/request/", request_magic_link, name="request_magic_link"),
    path("auth/magic-link/verify/", verify_magic_link, name="verify_magic_link"),
    path("auth/google/", google_auth, name="google_auth"),
    path("auth/logout/", logout, name="logout"),
    # User profile endpoints
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("sessions/", user_sessions, name="user_sessions"),
]
