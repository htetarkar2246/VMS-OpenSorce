from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserContact

User = get_user_model()


class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = [
            "id",
            "contact_type",
            "value",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    contacts = UserContactSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "name",
            "profile_photo",
            "phone",
            "role",
            "position",
            "join_date",
            "contacts",
        ]

    def create(self, validated_data):
        contacts_data = validated_data.pop("contacts", [])
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        for contact in contacts_data:
            UserContact.objects.create(user=user, **contact)

        return user


class UserSerializer(serializers.ModelSerializer):
    contacts = UserContactSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "profile_photo",
            "phone",
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
            "contacts",
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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)