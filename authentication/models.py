from datetime import timedelta

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
        extra_fields.setdefault("name", "System Administrator")
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

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Telegram username (e.g. @username)",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    position = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    join_date = models.DateField(
        null=True,
        blank=True,
    )

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

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name


class PasswordResetOTP(models.Model):
    """OTP for forgot password."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
    )

    otp = models.CharField(max_length=6)

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    OTP_TTL_MINUTES = 10

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["otp"]),
            models.Index(fields=["created_at"]),
        ]

    def is_expired(self):
        """Check whether the OTP has passed its validity window."""
        return (
            timezone.now()
            > self.created_at + timedelta(minutes=self.OTP_TTL_MINUTES)
        )

    def mark_used(self):
        """Mark the OTP as consumed so it cannot be reused."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"{self.user.email} - {self.otp}"
