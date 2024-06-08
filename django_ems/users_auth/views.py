from django.conf import settings
from rest_framework import generics, status, views
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken as SimpleJWTInvalidToken
from rest_framework_simplejwt.exceptions import TokenError as SimpleJWTTokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django_ems.users.models import User
from django_ems.users_auth.exceptions import Unauthorized, UnprocessableEntity
from django_ems.users_auth.serializers import UsersSerializer


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

        except AuthenticationFailed:
            raise Unauthorized("Invalid credentials.")

        # Get the access token and refresh token from serializer
        access_token: str = serializer.validated_data["access"]
        refresh_token: str = serializer.validated_data["refresh"]

        # Prepare the JSON response
        response = Response(
            data={
                "access_token": access_token,
            },
            status=status.HTTP_200_OK,
        )

        # Set refresh token as an HTTP-only cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT["SESSION_COOKIE"],
            value=refresh_token,
            expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
            secure=True,
            samesite=settings.SIMPLE_JWT["SESSION_COOKIE_SAMESITE"],
        )

        return response


class LogoutView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        try:
            refresh_token = request.COOKIES[settings.SIMPLE_JWT["SESSION_COOKIE"]]
            token = RefreshToken(refresh_token)
            token.blacklist()

        except KeyError:
            raise UnprocessableEntity("Session cookie is missing.", code="cookie")

        except (SimpleJWTInvalidToken, SimpleJWTTokenError):
            raise UnprocessableEntity("Session cookie is invalid or expired.")

        return Response(status=status.HTTP_204_NO_CONTENT)
