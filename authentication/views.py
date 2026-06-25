import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from utils.responses import success_response, error_response

from .models import PasswordResetOTP
from .serializers import (
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()

        return success_response(
            message="User registered successfully.",
            data=UserSerializer(user).data,
            status_code=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return success_response(
            message="Current user retrieved successfully.",
            data=UserSerializer(request.user).data,
        )

    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response(
            message="Profile updated successfully.",
            data=serializer.data,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")

        if not refresh:
            return error_response(
                message="Refresh token is required.",
                errors={
                    "refresh": [
                        "This field is required."
                    ]
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh).blacklist()

            return success_response(
                message="Logged out successfully.",
            )

        except Exception:
            return error_response(
                message="Invalid refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()

        if not user:
            return error_response(
                message="No user found with this email.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Invalidate previous unused OTPs
        PasswordResetOTP.objects.filter(
            user=user,
            is_used=False,
        ).update(is_used=True)

        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp,
        )

        send_mail(
            subject="VMS Password Reset OTP",
            message=(
                f"Hello {user.name},\n\n"
                f"Your One-Time Password (OTP) is: {otp}\n\n"
                "This OTP will expire in 10 minutes.\n"
                "If you did not request this password reset, please ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return success_response(
            message="OTP has been sent to your email.",
        )


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        user = User.objects.filter(email=email).first()

        if not user:
            return error_response(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        otp_obj = (
            PasswordResetOTP.objects.filter(
                user=user,
                otp=otp,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if otp_obj is None:
            return error_response(
                message="Invalid OTP.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if otp_obj.is_expired():
            return error_response(
                message="OTP has expired.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(
            message="OTP verified successfully.",
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        user = User.objects.filter(email=email).first()

        if not user:
            return error_response(
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        otp_obj = (
            PasswordResetOTP.objects.filter(
                user=user,
                otp=otp,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if otp_obj is None:
            return error_response(
                message="Invalid OTP.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if otp_obj.is_expired():
            return error_response(
                message="OTP has expired.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        return success_response(
            message="Password reset successfully.",
        )