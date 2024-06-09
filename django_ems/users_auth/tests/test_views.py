from typing import Any

from django.conf import settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

import pytest
from django_ems.users.models import User
from django_ems.users_auth.tests import _create_user_in_db

signup_path = reverse("users_auth:signup")
login_path = reverse("users_auth:login")
logout_path = reverse("users_auth:logout")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestSignupView:

    def test_signup_view(self, api_client: APIClient):
        request_body = {
            "name": "Demo",
            "email": "demo@aeroglobe.com",
            "password": "password123@",
            "mobile_number": "0321-9242194",
        }
        response: Response = api_client.post(path=signup_path, data=request_body)

        # Validate response
        assert response.status_code == 201
        assert response.data["name"] == request_body["name"]
        assert response.data["email"] == request_body["email"]
        assert response.data["mobile_number"] == request_body["mobile_number"]
        assert "id" in response.data
        assert "password" and "created_at" and "updated_at" not in response.data

        # Validate database
        assert User.objects.filter(id=response.data["id"]).exists() is True

    def test_signup_view_with_existing_email(self, api_client: APIClient):
        _, email, *_ = _create_user_in_db()

        request_body = {
            "name": "Demo",
            "email": email,
            "password": "password123@",
            "mobile_number": "0321-9242194",
        }
        response: Response = api_client.post(path=signup_path, data=request_body)

        # Validate response
        assert response.status_code == 400
        assert response.data == {
            "email": ["user with this email address already exists."]
        }

        # Validate database
        assert User.objects.all().count() == 1

    @pytest.mark.parametrize(
        "request_body, expected_status_code, expected_body",
        [
            (
                {"name": "Demo"},
                400,
                {
                    "email": ["This field is required."],
                    "password": ["This field is required."],
                    "mobile_number": ["This field is required."],
                },
            ),
            (
                {"email": "demo@aeroglobe.com"},
                400,
                {
                    "name": ["This field is required."],
                    "password": ["This field is required."],
                    "mobile_number": ["This field is required."],
                },
            ),
            (
                {"password": "pass1234"},
                400,
                {
                    "name": ["This field is required."],
                    "email": ["This field is required."],
                    "mobile_number": ["This field is required."],
                },
            ),
            (
                {"mobile_number": "0321-2105825"},
                400,
                {
                    "name": ["This field is required."],
                    "email": ["This field is required."],
                    "password": ["This field is required."],
                },
            ),
            (
                {"name": "Demo", "email": "demo@aeroglobe.com", "password": "pass1234"},
                400,
                {"mobile_number": ["This field is required."]},
            ),
            (
                {
                    "email": "demo@aeroglobe.com",
                    "password": "pass1234",
                    "mobile_number": "0321-2105825",
                },
                400,
                {"name": ["This field is required."]},
            ),
        ],
    )
    def test_signup_view_with_invalid_request_parameters(
        self,
        api_client: APIClient,
        request_body: dict[str, Any],
        expected_status_code: int,
        expected_body: dict[str, Any],
    ):
        response: Response = api_client.post(path=signup_path, data=request_body)
        assert response.status_code == expected_status_code
        assert response.data == expected_body


@pytest.mark.django_db
class TestLoginView:

    def test_login_view(self, api_client: APIClient):
        _, email, password, *_ = _create_user_in_db()
        request_body = {
            "email": email,
            "password": password,
        }
        response: Response = api_client.post(path=login_path, data=request_body)

        # Validate response
        assert response.status_code == 200
        assert "access_token" in response.data
        assert response.cookies.get(settings.SIMPLE_JWT["SESSION_COOKIE"]) is not None

    @pytest.mark.parametrize(
        "request_body",
        [
            {"email": "invalid-email@example.com", "password": "password123@"},
            {"email": "demo@aeroglobe.com", "password": "invalid-password"},
        ],
    )
    def test_login_view_with_invalid_credentials(
        self, api_client: APIClient, request_body: dict[str, str]
    ):
        _create_user_in_db()
        response: Response = api_client.post(login_path, data=request_body)

        assert response.status_code == 401
        assert "access_token" not in response.data
        assert response.cookies.get(settings.SIMPLE_JWT["SESSION_COOKIE"]) is None

    @pytest.mark.parametrize(
        "request_body, expected_body",
        [
            (
                {"email": "demo@aeroglobe.com"},
                {
                    "password": ["This field is required."],
                },
            ),
            (
                {"password": "password123@"},
                {
                    "email": ["This field is required."],
                },
            ),
        ],
    )
    def test_login_view_with_invalid_request_parameters(
        self,
        api_client: APIClient,
        request_body: dict[str, Any],
        expected_body: dict[str, Any],
    ):
        response: Response = api_client.post(path=login_path, data=request_body)
        assert response.status_code == 400
        assert response.data == expected_body


@pytest.mark.django_db
class TestLogoutView:

    def test_logout_view(self, api_client: APIClient):

        _, email, password, *_, user = _create_user_in_db()
        request_body = {
            "email": email,
            "password": password,
        }
        response: Response = api_client.post(path=login_path, data=request_body)
        assert response.status_code == 200

        # Process logout method
        api_client.force_authenticate(user)
        response: Response = api_client.post(path=logout_path)

        # Validate response
        assert response.status_code == 204
        assert response.data == None

    def test_logout_view_without_authorization(self, api_client: APIClient):

        _, email, password, *_ = _create_user_in_db()
        request_body = {
            "email": email,
            "password": password,
        }
        response: Response = api_client.post(path=login_path, data=request_body)
        assert response.status_code == 200

        # Process logout method
        response: Response = api_client.post(path=logout_path)

        # Validate response
        assert response.status_code == 401
        assert response.data == {
            "detail": "Authentication credentials were not provided."
        }
