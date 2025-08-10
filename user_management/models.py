from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import string


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # OAuth fields
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    avatar_url = models.URLField(blank=True, null=True)

    # User preferences
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class MagicLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="magic_links")
    token = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    is_signup = models.BooleanField(default=False)  # True for signup, False for login
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "magic_links"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Magic link for {self.email}"

    @classmethod
    def generate_token(cls):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(64))

    def is_valid(self):
        """Check if the magic link is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark the magic link as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()


class UserSession(models.Model):
    """Track user sessions for security purposes"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_method = models.CharField(
        max_length=20,
        choices=[
            ("magic_link", "Magic Link"),
            ("google_oauth", "Google OAuth"),
            ("password", "Password"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "user_sessions"
        unique_together = ["user", "session_key"]
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Session for {self.user.email} via {self.login_method}"
