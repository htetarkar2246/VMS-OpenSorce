from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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