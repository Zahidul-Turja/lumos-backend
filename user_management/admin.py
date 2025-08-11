# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, MagicLink, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "full_name",
        "is_email_verified",
        "is_active",
        "created_at",
    )
    list_filter = ("is_email_verified", "is_active", "is_staff", "created_at")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "avatar_url")},
        ),
        ("OAuth info", {"fields": ("google_id",), "classes": ("collapse",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important dates",
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        ("Verification", {"fields": ("is_email_verified",)}),
    )

    readonly_fields = ("created_at", "updated_at", "last_login", "date_joined")

    def full_name(self, obj):
        return obj.full_name or "-"

    full_name.short_description = "Full Name"


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "user_username",
        "is_signup",
        "is_used",
        "expires_at",
        "created_at",
    )
    list_filter = ("is_signup", "is_used", "created_at", "expires_at")
    search_fields = ("email", "user__email", "user__username")
    readonly_fields = ("token", "created_at", "used_at")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("user", "email", "is_signup")}),
        ("Token Info", {"fields": ("token", "expires_at")}),
        ("Status", {"fields": ("is_used", "used_at")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )

    def user_username(self, obj):
        return obj.user.username if obj.user else "-"

    user_username.short_description = "Username"
    user_username.admin_order_field = "user__username"

    def has_add_permission(self, request):
        # Prevent manual creation of magic links from admin
        return False


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user_email",
        "login_method",
        "ip_address",
        "browser_info",
        "is_active",
        "created_at",
        "last_activity",
    )
    list_filter = ("login_method", "is_active", "created_at")
    search_fields = ("user__email", "user__username", "ip_address")
    readonly_fields = ("session_key", "user_agent", "created_at", "last_activity")
    ordering = ("-last_activity",)

    fieldsets = (
        (None, {"fields": ("user", "login_method", "is_active")}),
        ("Session Info", {"fields": ("session_key", "ip_address")}),
        ("Browser Info", {"fields": ("user_agent",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "last_activity")}),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "User Email"
    user_email.admin_order_field = "user__email"

    def browser_info(self, obj):
        # Simple extraction from user agent
        ua = obj.user_agent.lower()
        if "chrome" in ua:
            browser = "Chrome"
        elif "firefox" in ua:
            browser = "Firefox"
        elif "safari" in ua:
            browser = "Safari"
        elif "edge" in ua:
            browser = "Edge"
        else:
            browser = "Unknown"
        return browser

    browser_info.short_description = "Browser"

    def has_add_permission(self, request):
        # Prevent manual creation of sessions from admin
        return False


# Customize admin site
admin.site.site_header = "Lumos Backend Administration"
admin.site.site_title = "Lumos Admin"
admin.site.index_title = "Welcome to Lumos Administration"
