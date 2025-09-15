from rest_framework import serializers
from django.contrib.auth import get_user_model
from user_management.models import MagicLink

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar_url",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_email_verified"]


class MagicLinkRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_signup = serializers.BooleanField(default=False)
    redirect_url = serializers.URLField(required=False)

    def validate_email(self, value):
        email = value.lower()
        is_signup = self.initial_data.get("is_signup", False)

        if is_signup:
            # For signup, email should not exist
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    "An account with this email already exists. Try logging in instead."
                )
        else:
            # For login, email should exist
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    "No account found with this email. Try signing up instead."
                )

        return email


class MagicLinkVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)

    def validate_token(self, value):
        try:
            magic_link = MagicLink.objects.get(token=value)
            if not magic_link.is_valid():
                raise serializers.ValidationError(
                    "This magic link has expired or been used."
                )
            return value
        except MagicLink.DoesNotExist:
            raise serializers.ValidationError("Invalid magic link.")


class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def validate_access_token(self, value):
        if not value:
            raise serializers.ValidationError("Access token is required.")
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]

    def validate_username(self, value):
        user = self.instance
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
