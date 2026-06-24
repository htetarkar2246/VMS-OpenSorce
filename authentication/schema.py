"""OpenAPI schema helpers for drf-spectacular."""

from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

from .serializers import UserSerializer


# Standard JWT token pair returned by login / refresh endpoints.
TokenPairSerializer = inline_serializer(
    name="TokenPair",
    fields={
        "access": serializers.CharField(),
        "refresh": serializers.CharField(),
    },
)

# Logout request body.
LogoutRequestSerializer = inline_serializer(
    name="LogoutRequest",
    fields={
        "refresh": serializers.CharField(
            help_text="Refresh token to blacklist on logout.",
        ),
    },
)


def envelope_serializer(data_serializer=None, *, name="ApiEnvelope"):
    """Build an OpenAPI schema for the standard API response envelope."""
    fields = {
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.DictField(allow_null=True, required=False),
    }
    if data_serializer is not None:
        fields["data"] = data_serializer(allow_null=True, required=False)
    else:
        fields["data"] = serializers.JSONField(allow_null=True, required=False)

    return inline_serializer(name=name, fields=fields)


UserEnvelopeSerializer = envelope_serializer(UserSerializer, name="UserEnvelope")
EmptyEnvelopeSerializer = envelope_serializer(name="EmptyEnvelope")
