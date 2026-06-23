from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

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
            "role",
            "position",
            "join_date",
            "job_description",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
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