from django.urls import path
from user_management.views import (
    RequestMagicLinkView,
    VerifyMagicLinkView,
    GoogleAuthView,
    LogoutView,
    UserProfileView,
    UserSessionsView,
)

user_urlpatterns = [
    path(
        "auth/magic-link/request/",
        RequestMagicLinkView.as_view(),
        name="request_magic_link",
    ),
    path(
        "auth/magic-link/verify/",
        VerifyMagicLinkView.as_view(),
        name="verify_magic_link",
    ),
    path("auth/google/", GoogleAuthView.as_view(), name="google_auth"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("sessions/", UserSessionsView.as_view(), name="user_sessions"),
]
