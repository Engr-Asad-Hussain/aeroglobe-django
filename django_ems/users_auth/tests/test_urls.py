from django.urls import resolve, reverse

from django_ems.users_auth import views


class TestUsersAuthUrls:
    def test_signup_url(self):
        url = reverse("users_auth:signup")
        resolver = resolve(url)

        assert resolver.route == "signup/"
        assert resolver.app_name == "users_auth"
        assert resolver.view_name == "users_auth:signup"
        assert resolver.func.view_class == views.SignupView

    def test_login_url(self):
        url = reverse("users_auth:login")
        resolver = resolve(url)

        assert resolver.route == "login/"
        assert resolver.app_name == "users_auth"
        assert resolver.view_name == "users_auth:login"
        assert resolver.func.view_class == views.LoginView

    def test_logout_url(self):
        url = reverse("users_auth:logout")
        resolver = resolve(url)

        assert resolver.route == "logout/"
        assert resolver.app_name == "users_auth"
        assert resolver.view_name == "users_auth:logout"
        assert resolver.func.view_class == views.LogoutView
