from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import PasswordResetOTP, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "name",
        "role",
        "position",
        "status",
        "phone",
        "telegram_username",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "role",
        "status",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "name",
        "phone",
        "telegram_username",
        "position",
    )

    ordering = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "name",
                    "profile_photo",
                    "phone",
                    "telegram_username",
                )
            },
        ),
        (
            "Organization Information",
            {
                "fields": (
                    "role",
                    "position",
                    "join_date",
                    "status",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "last_login",
        "created_at",
        "updated_at",
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "phone",
                    "telegram_username",
                    "role",
                    "position",
                    "join_date",
                    "status",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "otp",
        "is_used",
        "created_at",
    )

    list_filter = (
        "is_used",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__name",
        "otp",
    )

    readonly_fields = (
        "created_at",
    )