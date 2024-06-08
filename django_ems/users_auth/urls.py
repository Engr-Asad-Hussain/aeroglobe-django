from django.urls import path

from .views import LoginView, LogoutView, SignupView

app_name = "users_auth"
urlpatterns = [
    path("signup/", view=SignupView.as_view(), name="signup"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
]
