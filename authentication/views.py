import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import PasswordResetOTP
from .schema import (
    EmptyEnvelopeSerializer,
    LogoutRequestSerializer,
    TokenPairSerializer,
    UserEnvelopeSerializer,
)
from .serializers import (
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


def envelope(success=True, message="", data=None, errors=None):
    """Standard API response wrapper used across all auth endpoints."""
    return {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }


class RegisterView(generics.CreateAPIView):
    """Register a new volunteer account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        description=(
            "Create a new volunteer account. New users are assigned the MEMBER role "
            "by default; role cannot be set during registration."
        ),
        auth=[],
        responses={
            201: UserEnvelopeSerializer,
            400: UserEnvelopeSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                envelope(
                    True,
                    "User registered successfully",
                    UserSerializer(user).data,
                ),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(TokenObtainPairView):
    """Obtain JWT access and refresh tokens."""

    @extend_schema(
        tags=["Authentication"],
        summary="Login",
        description="Authenticate with username and password to receive JWT tokens.",
        auth=[],
        responses={
            200: TokenPairSerializer,
            401: OpenApiResponse(description="Invalid credentials."),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshAPIView(TokenRefreshView):
    """Refresh an expired access token."""

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh access token",
        description="Exchange a valid refresh token for a new access token.",
        auth=[],
        responses={
            200: TokenPairSerializer,
            401: OpenApiResponse(description="Invalid or expired refresh token."),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(APIView):
    """Retrieve or update the authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Get current user profile",
        responses={200: UserEnvelopeSerializer},
    )
    def get(self, request):
        return Response(
            envelope(
                True,
                "Current user retrieved successfully",
                UserSerializer(request.user).data,
            )
        )

    @extend_schema(
        tags=["Authentication"],
        summary="Update current user profile",
        description="Partial update of profile fields. Role and status are read-only.",
        request=UserSerializer,
        responses={
            200: UserEnvelopeSerializer,
            400: UserEnvelopeSerializer,
        },
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                envelope(True, "User updated successfully", serializer.data)
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(APIView):
    """Blacklist a refresh token to end the session."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Logout",
        description="Blacklist the provided refresh token. Requires a valid access token.",
        request=LogoutRequestSerializer,
        responses={
            200: EmptyEnvelopeSerializer,
            400: EmptyEnvelopeSerializer,
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                envelope(
                    False,
                    "Refresh token is required",
                    None,
                    {"refresh": ["This field is required."]},
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            envelope(True, "Logged out successfully"),
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    """Send a one-time password (OTP) to the user's email for password reset."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Request password reset OTP",
        description="Sends a 6-digit OTP to the registered email. The OTP expires in 10 minutes.",
        auth=[],
        request=ForgotPasswordSerializer,
        responses={
            200: EmptyEnvelopeSerializer,
            400: EmptyEnvelopeSerializer,
            404: EmptyEnvelopeSerializer,
        },
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                envelope(False, "Validation failed", None, serializer.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                envelope(
                    False,
                    "No user found with this email",
                    None,
                    {"email": ["User not found."]},
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            subject="UYA VMS Password Reset OTP",
            message=f"Your password reset OTP is {otp}. It expires in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(envelope(True, "OTP sent to your email"))


class VerifyOTPView(APIView):
    """Verify a password-reset OTP without changing the password."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Verify password reset OTP",
        auth=[],
        request=VerifyOTPSerializer,
        responses={
            200: EmptyEnvelopeSerializer,
            400: EmptyEnvelopeSerializer,
        },
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                envelope(False, "Validation failed", None, serializer.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                envelope(False, "Invalid email or OTP"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp,
            is_used=False,
        ).last()

        if not otp_obj or otp_obj.is_expired():
            return Response(
                envelope(False, "Invalid or expired OTP"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(envelope(True, "OTP verified successfully"))


class ResetPasswordView(APIView):
    """Reset the user's password using a verified OTP."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Reset password",
        description="Set a new password after verifying the OTP sent to the user's email.",
        auth=[],
        request=ResetPasswordSerializer,
        responses={
            200: EmptyEnvelopeSerializer,
            400: EmptyEnvelopeSerializer,
        },
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                envelope(False, "Validation failed", None, serializer.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                envelope(False, "Invalid email or OTP"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp,
            is_used=False,
        ).last()

        if not otp_obj or otp_obj.is_expired():
            return Response(
                envelope(False, "Invalid or expired OTP"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return Response(envelope(True, "Password reset successfully"))
