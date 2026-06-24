from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user model for the Volunteer Management System."""

    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        LEADER = "LEADER", "Leader"
        MEMBER = "MEMBER", "Member"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        RESIGNED = "RESIGNED", "Resigned"
        REMOVED = "REMOVED", "Removed"

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    position = models.CharField(max_length=150, blank=True)
    join_date = models.DateField(null=True, blank=True)
    job_description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    def __str__(self):
        return self.get_full_name() or self.username


class PasswordResetOTP(models.Model):
    """One-time password issued for the forgot-password flow. Expires after 10 minutes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
    )
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    OTP_TTL_MINUTES = 10

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=self.OTP_TTL_MINUTES)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
