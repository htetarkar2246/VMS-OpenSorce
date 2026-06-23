from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


def envelope(success=True, message="", data=None, errors=None):
    return {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                envelope(
                    True,
                    "User registered successfully",
                    UserSerializer(user).data,
                    None,
                ),
                status=status.HTTP_201_CREATED,
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            envelope(
                True,
                "Current user retrieved successfully",
                UserSerializer(request.user).data,
                None,
            )
        )

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                envelope(True, "User updated successfully", serializer.data, None)
            )

        return Response(
            envelope(False, "Validation failed", None, serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                envelope(False, "Refresh token is required", None, {
                    "refresh": ["This field is required."]
                }),
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            envelope(True, "Logged out successfully", None, None),
            status=status.HTTP_200_OK,
        )