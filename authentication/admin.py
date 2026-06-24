from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import PasswordResetOTP, User, UserContact


class UserContactInline(admin.TabularInline):
    model = UserContact
    extra = 1


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    inlines = [UserContactInline]

    list_display = (
        "id",
        "email",
        "name",
        "role",
        "position",
        "status",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = ("role", "status", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "name", "phone", "position")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name", "profile_photo", "phone")}),
        ("UYA Info", {"fields": ("role", "position", "join_date", "status")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    readonly_fields = ("last_login", "created_at", "updated_at")

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
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(UserContact)
class UserContactAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "contact_type", "value", "is_primary")
    list_filter = ("contact_type", "is_primary")
    search_fields = ("user__name", "user__email", "value")


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "otp", "is_used", "created_at")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "otp")