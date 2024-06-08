from typing import TypedDict

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from django_ems.users.models import User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email", "password", "mobile_number")
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "email": {"required": True},
            "name": {"required": True},
            "mobile_number": {"required": True},
        }

    class _SignupUserRequestParameters(TypedDict):
        name: str
        email: str
        password: str
        mobile_number: str

    def create(self, validated_data: _SignupUserRequestParameters) -> User:
        return User.objects.create_user(
            name=validated_data["name"],
            email=validated_data["email"],
            password=validated_data["password"],
            mobile_number=validated_data["mobile_number"],
        )
