from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ForgotPasswordView,
    LogoutView,
    MeView,
    RegisterView,
    ResetPasswordView,
    UserContactDetailView,
    UserContactListCreateView,
    VerifyOTPView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),

    path("contacts/", UserContactListCreateView.as_view(), name="user-contact-list-create"),
    path("contacts/<int:pk>/", UserContactDetailView.as_view(), name="user-contact-detail"),

    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]