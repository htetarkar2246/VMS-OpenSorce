from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for new user registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Minimum 8 characters.",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "telegram_username",
            "phone",
            "position",
            "join_date",
            "job_description",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "username": {"help_text": "Unique username for login."},
            "email": {"help_text": "Unique email address."},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profile data."""

    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "avatar",
            "username",
            "email",
            "first_name",
            "last_name",
            "telegram_username",
            "phone",
            "role",
            "position",
            "join_date",
            "job_description",
            "status",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "status", "date_joined"]


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Email address of the account to reset.")


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, help_text="6-digit OTP sent to email.")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, help_text="6-digit OTP sent to email.")
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="New password (minimum 8 characters).",
    )
