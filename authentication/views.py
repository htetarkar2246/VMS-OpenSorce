import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from utils.responses import error_response, success_response

from .models import PasswordResetOTP
from .serializers import (
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


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
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return success_response(
            message="Current user retrieved successfully.",
            data=UserSerializer(request.user).data,
        )

    def put(self, request):
        serializer = self.serializer_class(
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


class UserManagementViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()

        user = self.request.user
        queryset = User.objects.filter(is_active=True)

        if user.is_superuser or user.role == "MANAGER":
            return queryset

        if user.role == "SUPERVISOR":
            return queryset.filter(
                Q(team_memberships__team__department__supervisor=user)
                | Q(team_memberships__team__department__coordinator=user)
            ).distinct()

        if user.role == "LEADER":
            return queryset.filter(
                Q(team_memberships__team__leader=user)
                | Q(team_memberships__team__assistant_leader=user)
            ).distinct()

        return queryset.filter(id=user.id)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response("Users retrieved successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("User retrieved successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return success_response("User updated successfully.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        if request.user.id == user.id:
            return error_response(
                message="You cannot remove your own account.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])

        return success_response(message="User removed successfully.")


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        refresh = serializer.validated_data["refresh"]

        try:
            RefreshToken(refresh).blacklist()
            return success_response(message="Logged out successfully.")

        except TokenError:
            return error_response(
                message="Invalid refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

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

        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)

        try:
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
        except Exception:
            return error_response(
                message="Failed to send OTP email.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return success_response(
            message="OTP has been sent to your email.",
            status_code=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

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
            PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False)
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

        return success_response(message="OTP verified successfully.")


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

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
            PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False)
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

        if hasattr(otp_obj, "mark_used"):
            otp_obj.mark_used()
        else:
            otp_obj.is_used = True
            otp_obj.save(update_fields=["is_used"])

        return success_response(message="Password reset successfully.")

