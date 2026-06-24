import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PasswordResetOTP, UserContact
from .serializers import (
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserContactSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


def envelope(success=True, message="", data=None, errors=None):
    return {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                envelope(True, "User registered successfully", UserSerializer(user).data),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            envelope(True, "Current user retrieved successfully", UserSerializer(request.user).data)
        )

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(envelope(True, "User updated successfully", serializer.data))

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                envelope(False, "Refresh token is required", None, {"refresh": ["This field is required."]}),
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(envelope(True, "Logged out successfully"))


class UserContactListCreateView(generics.ListCreateAPIView):
    serializer_class = UserContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserContact.objects.filter(user=self.request.user)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(envelope(False, "Validation failed", None, serializer.errors), status=400)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(envelope(False, "No user found with this email"), status=404)

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
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(envelope(False, "Validation failed", None, serializer.errors), status=400)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        otp = serializer.validated_data["otp"]

        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).last() if user else None

        if not otp_obj or otp_obj.is_expired():
            return Response(envelope(False, "Invalid or expired OTP"), status=400)

        return Response(envelope(True, "OTP verified successfully"))


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(envelope(False, "Validation failed", None, serializer.errors), status=400)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        otp = serializer.validated_data["otp"]

        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).last() if user else None

        if not otp_obj or otp_obj.is_expired():
            return Response(envelope(False, "Invalid or expired OTP"), status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return Response(envelope(True, "Password reset successfully"))