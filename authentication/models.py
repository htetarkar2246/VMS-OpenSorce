from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager that uses email instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("name", "System Admin")
        extra_fields.setdefault("role", User.Role.MANAGER)
        extra_fields.setdefault("status", User.Status.ACTIVE)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for the Volunteer Management System."""

    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        LEADER = "LEADER", "Leader"
        MEMBER = "MEMBER", "Member"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        RESIGNED = "RESIGNED", "Resigned"
        REMOVED = "REMOVED", "Removed"

    username = None
    first_name = None
    last_name = None
    date_joined = None

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    position = models.CharField(max_length=150, blank=True, null=True)
    join_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.name


class UserContact(models.Model):
    """Contact methods such as Telegram, Discord, Facebook, LinkedIn, etc."""

    class ContactType(models.TextChoices):
        TELEGRAM = "TELEGRAM", "Telegram"
        DISCORD = "DISCORD", "Discord"
        FACEBOOK = "FACEBOOK", "Facebook"
        LINKEDIN = "LINKEDIN", "LinkedIn"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    contact_type = models.CharField(max_length=20, choices=ContactType.choices)
    value = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "contact_type", "value")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["contact_type"]),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.contact_type}: {self.value}"


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