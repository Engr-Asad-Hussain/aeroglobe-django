from typing import Tuple

from django_ems.events.models import Events


def _create_event_in_db(
    *,
    title: str = "Summer Vacations",
    description: str = "Yahoo! Summar vacations will start from next weekend.",
    date: str = "2024-05-13",
    location: str = "Karachi, Pakistan",
    owner_id: int,
) -> Tuple[str, str, str, str, Events]:
    return (
        title,
        description,
        date,
        location,
        Events.objects.create(
            title=title,
            description=description,
            date=date,
            location=location,
            owner_id=owner_id,
        ),
    )
