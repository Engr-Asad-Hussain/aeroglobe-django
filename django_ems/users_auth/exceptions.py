from rest_framework import status, views
from rest_framework.exceptions import APIException, NotAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken as SimpleJWTInvalidToken
from rest_framework_simplejwt.exceptions import TokenError as SimpleJWTTokenError


class Unauthorized(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, detail: str, code: str = "unauthorized"):
        super().__init__(detail, code)


class UnprocessableEntity(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, detail: str, code: str | None = None):
        super().__init__(detail, code)


def app_exception_handler(exc, context):
    response = views.exception_handler(exc, context)

    if isinstance(exc, (SimpleJWTInvalidToken, SimpleJWTTokenError)):
        response.data = {
            "detail": "Token is invalid or expired.",
        }

    if isinstance(exc, NotAuthenticated):
        response.status_code = 401

    return response
