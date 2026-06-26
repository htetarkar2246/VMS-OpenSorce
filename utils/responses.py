"""Shared API response envelopes used across the project."""

from django.utils import timezone
from rest_framework.response import Response


def success_response(
    message="Success.",
    data=None,
    status_code=200,
):
    """Return a consistent success payload for API endpoints."""
    return Response(
        {
            "success": True,
            "status_code": status_code,
            "message": message,
            "data": data,
            "errors": None,
            "timestamp": timezone.now().isoformat(),
        },
        status=status_code,
    )


def error_response(
    message="Request failed.",
    errors=None,
    status_code=400,
):
    """Return a consistent error payload for API endpoints."""
    return Response(
        {
            "success": False,
            "status_code": status_code,
            "message": message,
            "data": None,
            "errors": errors,
            "timestamp": timezone.now().isoformat(),
        },
        status=status_code,
    )
