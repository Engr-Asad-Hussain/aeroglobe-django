from typing import Tuple

from django_ems.users.models import User


def _create_user_in_db(
    *,
    name: str = "Demo",
    email: str = "demo@aeroglobe.com",
    password: str = "password123@",
    mobile_number: str = "0321-9242194",
) -> Tuple[str, str, str, str, User]:
    return (
        name,
        email,
        password,
        mobile_number,
        User.objects.create_user(
            name=name, email=email, password=password, mobile_number=mobile_number
        ),
    )
