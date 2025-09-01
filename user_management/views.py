from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
import logging

from .models import MagicLink, UserSession
from .serializers import (
    UserSerializer,
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
    GoogleAuthSerializer,
    UserProfileUpdateSerializer,
)
from user_management.utils import get_client_ip, get_user_agent

User = get_user_model()
logger = logging.getLogger(__name__)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserSerializer


class RequestMagicLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MagicLinkRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        is_signup = serializer.validated_data["is_signup"]
        redirect_url = serializer.validated_data.get("redirect_url", "")

        try:
            # Get or create user
            if is_signup:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": email.split("@")[0],
                        "is_email_verified": False,
                    },
                )
            else:
                user = User.objects.get(email=email)

            # Create magic link
            magic_link = MagicLink.objects.create(
                user=user,
                email=email,
                token=MagicLink.generate_token(),
                is_signup=is_signup,
                expires_at=timezone.now() + timedelta(minutes=15),
            )

            # Send email
            magic_url = f"{settings.FRONTEND_URL}/auth/verify?token={magic_link.token}"
            if redirect_url:
                magic_url += f"&redirect={redirect_url}"

            subject = (
                "Sign up for your account" if is_signup else "Sign in to your account"
            )
            message = f"""
            Hello!
            
            {'Welcome! Click the link below to complete your signup:' if is_signup else 'Click the link below to sign in:'}
            
            {magic_url}
            
            This link will expire in 15 minutes.
            
            If you didn't request this, please ignore this email.
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response(
                {
                    "message": f"Magic link sent to {email}",
                    "expires_in": 900,  # 15 minutes in seconds
                }
            )

        except Exception as e:
            logger.error(f"Error sending magic link: {str(e)}")
            return Response(
                {"error": "Failed to send magic link. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyMagicLinkView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MagicLinkVerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]

        try:
            magic_link = MagicLink.objects.get(token=token)

            if not magic_link.is_valid():
                return Response(
                    {"error": "Magic link has expired or been used"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = magic_link.user

            # Mark email as verified if it's a signup
            if magic_link.is_signup:
                user.is_email_verified = True
                user.save()

            # Mark magic link as used
            magic_link.mark_as_used()

            # Create session record
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key or "api_session",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                login_method="magic_link",
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "message": "Successfully authenticated",
                }
            )

        except MagicLink.DoesNotExist:
            return Response(
                {"error": "Invalid magic link"}, status=status.HTTP_400_BAD_REQUEST
            )


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        access_token = serializer.validated_data["access_token"]

        try:
            # Verify token with Google
            google_response = requests.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
            )

            if google_response.status_code != 200:
                return Response(
                    {"error": "Invalid Google access token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            google_data = google_response.json()

            # Extract user info
            email = google_data.get("email")
            google_id = google_data.get("id")
            first_name = google_data.get("given_name", "")
            last_name = google_data.get("family_name", "")
            avatar_url = google_data.get("picture", "")

            if not email:
                return Response(
                    {"error": "Email not provided by Google"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "first_name": first_name,
                    "last_name": last_name,
                    "google_id": google_id,
                    "avatar_url": avatar_url,
                    "is_email_verified": True,  # Google emails are verified
                },
            )

            # Update user info if needed
            if not created and not user.google_id:
                user.google_id = google_id
                user.avatar_url = avatar_url or user.avatar_url
                user.is_email_verified = True
                user.save()

            # Create session record
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key or "api_session",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                login_method="google_oauth",
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "message": "Successfully authenticated with Google",
                    "is_new_user": created,
                }
            )

        except Exception as e:
            logger.error(f"Google auth error: {str(e)}")
            return Response(
                {"error": "Authentication failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Mark session as inactive
            UserSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key or "api_session",
            ).update(is_active=False)

            # If refresh token is provided, blacklist it
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass  # Token might already be invalid

            return Response({"message": "Successfully logged out"})

        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": "Logout failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = UserSession.objects.filter(
            user=request.user, is_active=True
        ).order_by("-last_activity")

        session_data = []
        for session in sessions:
            session_data.append(
                {
                    "id": session.id,
                    "login_method": session.login_method,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent[:100],
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "is_current": session.session_key
                    == (request.session.session_key or "api_session"),
                }
            )

        return Response({"sessions": session_data})
