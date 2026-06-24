from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import PasswordResetOTP, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "status", "is_staff")
    list_filter = ("role", "status", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        (
            "VMS Profile",
            {
                "fields": (
                    "avatar",
                    "telegram_username",
                    "phone",
                    "role",
                    "position",
                    "join_date",
                    "job_description",
                    "status",
                ),
            },
        ),
    )


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "is_used", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__email", "user__username")
    readonly_fields = ("created_at",)
