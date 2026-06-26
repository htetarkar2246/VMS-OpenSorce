from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


def validate_profile_image(file):
    """Validate uploaded profile photos before they reach storage."""
    if not file:
        return file

    allowed_content_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    if file.content_type not in allowed_content_types:
        raise serializers.ValidationError(
            "Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    max_size = 2 * 1024 * 1024  # 2 MB

    if file.size > max_size:
        raise serializers.ValidationError(
            "Profile photo size must not exceed 2MB."
        )

    return file


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer used for public user registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "name",
            "profile_photo",
            "phone",
            "telegram_username",
            "role",
            "position",
            "join_date",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_profile_photo(self, value):
        return validate_profile_image(value)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user profile data."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "profile_photo",
            "phone",
            "telegram_username",
            "role",
            "position",
            "join_date",
            "status",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "role",
            "status",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]

    def validate_profile_photo(self, value):
        return validate_profile_image(value)


class ForgotPasswordSerializer(serializers.Serializer):
    """Collect the email address for password reset flow."""

    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    """Validate the email and OTP pair submitted by the user."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    """Accept the verified OTP and a new password."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
