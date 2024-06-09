from pprint import pprint
from typing import Any, Callable, Tuple

from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

import pytest
from django_ems.events.models import Events
from django_ems.events.tests import _create_event_in_db
from django_ems.users_auth.tests import _create_user_in_db

# Helper Functions
events_path = reverse("events:events-list")
events_detail_path: Callable[[int], str] = lambda pk: reverse(
    "events:events-detail", kwargs={"pk": pk}
)
events_attend_path: Callable[[int], str] = lambda pk: reverse(
    "events:events-attendees", kwargs={"pk": pk}
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestCreateEventView:

    def test_create_event(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        api_client.force_authenticate(user)

        request_body = {
            "title": "Summer Vacations",
            "description": "Yahoo! Summar vacations will start from next weekend.",
            "date": "2024-05-13",
            "location": "Karachi, Pakistan",
        }
        response: Response = api_client.post(path=events_path, data=request_body)

        # Validate response
        assert response.status_code == 201
        assert response.data["title"] == request_body["title"]
        assert response.data["description"] == request_body["description"]
        assert response.data["date"] == request_body["date"]
        assert response.data["location"] == request_body["location"]
        assert response.data["attendees"] == []
        assert tuple(response.data.keys()) == (
            "id",
            "title",
            "description",
            "date",
            "location",
            "created_at",
            "updated_at",
            "attendees",
        )

        # Validate database
        event = Events.objects.filter(id=response.data["id"]).first()
        assert event is not None
        assert event.owner_id == user.id

    def test_create_event_without_authorization_token(self, api_client: APIClient):
        request_body = {
            "title": "Summer Vacations",
            "description": "Yahoo! Summar vacations will start from next weekend.",
            "date": "2024-05-13",
            "location": "Karachi, Pakistan",
        }

        response: Response = api_client.post(path=events_path, data=request_body)

        # Validate response
        assert response.status_code == 401
        assert response.data == {
            "detail": "Authentication credentials were not provided."
        }

    @pytest.mark.parametrize(
        "request_body, expected_body",
        [
            (
                {
                    "title": "Summer Vacations",
                },
                {
                    "description": ["This field is required."],
                    "date": ["This field is required."],
                    "location": ["This field is required."],
                },
            ),
            (
                {
                    "description": "Yahoo! Summar vacations will start from next weekend.",
                },
                {
                    "title": ["This field is required."],
                    "date": ["This field is required."],
                    "location": ["This field is required."],
                },
            ),
            (
                {
                    "date": "2024-05-13",
                },
                {
                    "title": ["This field is required."],
                    "description": ["This field is required."],
                    "location": ["This field is required."],
                },
            ),
            (
                {
                    "location": "Karachi, Pakistan",
                },
                {
                    "title": ["This field is required."],
                    "description": ["This field is required."],
                    "date": ["This field is required."],
                },
            ),
            (
                {
                    "title": "Summer Vacations",
                    "description": "Yahoo! Summar vacations will start from next weekend.",
                    "date": "invalid-date",
                    "location": "Karachi, Pakistan",
                },
                {
                    "date": [
                        "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
                    ]
                },
            ),
        ],
    )
    def test_create_event_with_invalid_request_parameters(
        self,
        api_client: APIClient,
        request_body: dict[str, Any],
        expected_body: dict[str, Any],
    ):
        *_, user = _create_user_in_db()
        api_client.force_authenticate(user)

        response: Response = api_client.post(path=events_path, data=request_body)
        assert response.status_code == 400
        assert response.data == expected_body


@pytest.mark.django_db
class TestUpdateEventView:

    def test_update_event_by_owner(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        api_client.force_authenticate(user)

        request_body = {
            "title": "Compliance",
            "description": "Security and compliance reports needs to be fix.",
            "date": "2024-06-18",
            "location": "British Columbia, Canada",
        }
        pk = event.id
        response: Response = api_client.put(
            path=events_detail_path(pk), data=request_body
        )

        # Validate response
        assert response.status_code == 200
        assert response.data["id"] == pk
        assert response.data["title"] == request_body["title"]
        assert response.data["description"] == request_body["description"]
        assert response.data["date"] == request_body["date"]
        assert response.data["location"] == request_body["location"]
        assert response.data["attendees"] == []
        assert tuple(response.data.keys()) == (
            "id",
            "title",
            "description",
            "date",
            "location",
            "created_at",
            "updated_at",
            "attendees",
        )

        # Validate database
        event = Events.objects.filter(id=response.data["id"]).first()
        assert event is not None
        assert event.owner_id == user.id

    def test_update_event_by_anonymous(self, api_client: APIClient):
        *_, user1 = _create_user_in_db(email="demo1@aeroglobe.com")
        *_, user2 = _create_user_in_db(email="demo2@aeroglobe.com")
        *_, event = _create_event_in_db(owner_id=user1.id)

        api_client.force_authenticate(user2)

        request_body = {
            "title": "Compliance",
            "description": "Security and compliance reports needs to be fix.",
            "date": "2024-06-18",
            "location": "British Columbia, Canada",
        }
        pk = event.id
        response: Response = api_client.put(
            path=events_detail_path(pk), data=request_body
        )

        # Validate response
        assert response.status_code == 403
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }

    def test_update_event_without_authorization_token(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        request_body = {
            "title": "Compliance",
            "description": "Security and compliance reports needs to be fix.",
            "date": "2024-06-18",
            "location": "British Columbia, Canada",
        }
        pk = event.id
        response: Response = api_client.put(
            path=events_detail_path(pk), data=request_body
        )

        # Validate response
        assert response.status_code == 401
        assert response.data == {
            "detail": "Authentication credentials were not provided."
        }

    @pytest.mark.parametrize(
        "request_body, expected_body",
        [
            (
                {
                    "title": "Summer Vacations",
                },
                {
                    "description": ["This field is required."],
                    "date": ["This field is required."],
                    "location": ["This field is required."],
                },
            ),
            (
                {
                    "description": "Yahoo! Summar vacations will start from next weekend.",
                },
                {
                    "title": ["This field is required."],
                    "date": ["This field is required."],
                    "location": ["This field is required."],
                },
            ),
            (
                {
                    "date": "2024-05-13",
                },
                {
                    "title": ["This field is required."],
                    "description": ["This field is required."],
                    "location": ["This field is required."],
                },
            ),
            (
                {
                    "location": "Karachi, Pakistan",
                },
                {
                    "title": ["This field is required."],
                    "description": ["This field is required."],
                    "date": ["This field is required."],
                },
            ),
            (
                {
                    "title": "Summer Vacations",
                    "description": "Yahoo! Summar vacations will start from next weekend.",
                    "date": "invalid-date",
                    "location": "Karachi, Pakistan",
                },
                {
                    "date": [
                        "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
                    ]
                },
            ),
        ],
    )
    def test_update_event_with_invalid_request_parameters(
        self,
        api_client: APIClient,
        request_body: dict[str, Any],
        expected_body: dict[str, Any],
    ):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        api_client.force_authenticate(user)

        pk = event.id
        response: Response = api_client.put(
            path=events_detail_path(pk), data=request_body
        )

        assert response.status_code == 400
        assert response.data == expected_body


@pytest.mark.django_db
class TestDeleteEventView:

    def test_delete_event_by_owner(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        api_client.force_authenticate(user)

        pk = event.id
        response: Response = api_client.delete(path=events_detail_path(pk))

        # Validate response
        assert response.status_code == 204
        assert response.data == None

        # Validate database
        event = Events.objects.filter(id=pk).first()
        assert event is None

    def test_delete_event_by_anonymous(self, api_client: APIClient):
        *_, user1 = _create_user_in_db(email="demo1@aeroglobe.com")
        *_, user2 = _create_user_in_db(email="demo2@aeroglobe.com")
        *_, event = _create_event_in_db(owner_id=user1.id)

        api_client.force_authenticate(user2)

        pk = event.id
        response: Response = api_client.delete(path=events_detail_path(pk))

        # Validate response
        assert response.status_code == 403
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }

    def test_delete_event_without_authorization_token(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        pk = event.id
        response: Response = api_client.delete(path=events_path + f"{pk}/")

        # Validate response
        assert response.status_code == 401
        assert response.data == {
            "detail": "Authentication credentials were not provided."
        }


@pytest.mark.django_db
class TestDetailEventView:

    def test_detail_event_with_authorization(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        api_client.force_authenticate(user)

        pk = event.id
        response: Response = api_client.get(path=events_detail_path(pk))

        # Validate response
        # TODO: owner?
        assert response.status_code == 200
        assert response.data == {
            "id": pk,
            "title": event.title,
            "description": event.description,
            "date": event.date,
            "location": event.location,
            "created_at": (event.created_at).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
            "updated_at": (event.updated_at).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
            "attendees": [],
        }

    def test_detail_event_without_authorization(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        pk = event.id
        response: Response = api_client.get(path=events_detail_path(pk))

        # Validate response
        # TODO: owner?
        assert response.status_code == 200
        assert response.data == {
            "id": pk,
            "title": event.title,
            "description": event.description,
            "date": event.date,
            "location": event.location,
            "created_at": (event.created_at).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
            "updated_at": (event.updated_at).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
            "attendees": [],
        }


@pytest.mark.django_db
class TestListEventView:

    def test_list_event(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        api_client.force_authenticate(user)
        response: Response = api_client.get(path=events_path)

        # Validate response
        assert response.status_code == 200
        assert response.data == {
            "page": 1,
            "page_size": 3,
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": event.date,
                    "location": event.location,
                    "created_at": (event.created_at).strftime("%Y-%m-%dT%H:%M:%S.%f")
                    + "Z",
                    "updated_at": (event.updated_at).strftime("%Y-%m-%dT%H:%M:%S.%f")
                    + "Z",
                    "attendees": [],
                }
            ],
        }

    def test_list_event_with_pagination(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        events = [_create_event_in_db(owner_id=user.id)[4] for _ in range(1, 8)]

        def _get_event(event: Events):
            return {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "date": event.date,
                "location": event.location,
                "created_at": event.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updated_at": event.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "attendees": [],
            }

        api_client.force_authenticate(user)
        response: Response = api_client.get(path=events_path)

        # Validate response
        assert response.status_code == 200
        assert response.data == {
            "page": 1,
            "page_size": 3,
            "count": 7,
            "next": f"http://testserver{events_path}?page=2",
            "previous": None,
            "results": [_get_event(event) for event in events[0:3]],
        }

        # Request with query parameters
        response: Response = api_client.get(path=events_path + "?page=2")

        # Validate response
        assert response.status_code == 200
        assert response.data == {
            "page": 2,
            "page_size": 3,
            "count": 7,
            "next": f"http://testserver{events_path}?page=3",
            "previous": f"http://testserver{events_path}",
            "results": [_get_event(event) for event in events[3:6]],
        }

        # Request with query parameters
        response: Response = api_client.get(path=events_path + "?page=3")

        # Validate response
        assert response.status_code == 200
        assert response.data == {
            "page": 3,
            "page_size": 3,
            "count": 7,
            "next": None,
            "previous": f"http://testserver{events_path}?page=2",
            "results": [_get_event(event) for event in events[6:]],
        }

    def test_list_event_without_authorization(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        response: Response = api_client.get(path=events_path)

        # Validate response
        assert response.status_code == 200
        assert response.data == {
            "page": 1,
            "page_size": 3,
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": event.date,
                    "location": event.location,
                    "created_at": (event.created_at).strftime("%Y-%m-%dT%H:%M:%S.%f")
                    + "Z",
                    "updated_at": (event.updated_at).strftime("%Y-%m-%dT%H:%M:%S.%f")
                    + "Z",
                    "attendees": [],
                }
            ],
        }

    # TODO: Add test for paginated items


@pytest.mark.django_db
class TestAttendEventView:

    def test_attend_event_created_by_owner(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        api_client.force_authenticate(user)

        pk = event.id
        response: Response = api_client.post(path=events_attend_path(pk))

        # Validate response
        assert response.status_code == 201
        assert response.data == {"detail": "You have been added to the event."}

        # Validate database
        assert user in event.attendees.all()

    def test_attend_event_created_by_anonymous(self, api_client: APIClient):
        *_, user1 = _create_user_in_db(email="demo1@aeroglobe.com")
        *_, user2 = _create_user_in_db(email="demo2@aeroglobe.com")
        *_, event = _create_event_in_db(owner_id=user1.id)

        api_client.force_authenticate(user2)

        pk = event.id
        response: Response = api_client.post(path=events_attend_path(pk))

        # Validate response
        assert response.status_code == 201
        assert response.data == {"detail": "You have been added to the event."}

        # Validate database
        assert user2 in event.attendees.all()

    def test_attend_event_without_authorization(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)

        pk = event.id
        response: Response = api_client.post(path=events_attend_path(pk))

        # Validate response
        assert response.status_code == 401
        assert response.data == {
            "detail": "Authentication credentials were not provided."
        }


@pytest.mark.django_db
class TestDropEventView:

    def test_drop_event(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)
        event.attendees.add(user)

        api_client.force_authenticate(user)

        pk = event.id
        response: Response = api_client.delete(path=events_attend_path(pk))

        # Validate response
        assert response.status_code == 200
        assert response.data == {"detail": "You have been removed from the event."}

        # Validate database
        assert user not in event.attendees.all()

    def test_drop_event_without_authorization(self, api_client: APIClient):
        *_, user = _create_user_in_db()
        *_, event = _create_event_in_db(owner_id=user.id)
        event.attendees.add(user)

        pk = event.id
        response: Response = api_client.delete(path=events_attend_path(pk))

        # Validate response
        assert response.status_code == 401
        assert response.data == {
            "detail": "Authentication credentials were not provided."
        }
