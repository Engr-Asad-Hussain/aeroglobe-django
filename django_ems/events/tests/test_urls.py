from django.urls import resolve, reverse

from django_ems.events import views


class TestEventsUrls:
    def test_events_list_url(self):
        url = reverse("events:events-list")
        resolver = resolve(url)

        assert resolver.app_name == "events"
        assert resolver.view_name == "events:events-list"
        assert resolver.route == "^events/$"
        assert resolver.func.cls == views.EventsViewSet
        assert resolver.func.actions == {
            "get": "list",
            "head": "list",
            "post": "create",
        }

    def test_events_detail_url(self):
        url = reverse("events:events-detail", kwargs={"pk": 1})
        resolver = resolve(url)

        assert resolver.app_name == "events"
        assert resolver.view_name == "events:events-detail"
        assert resolver.route == "^events/(?P<pk>[^/.]+)/$"
        assert resolver.func.cls == views.EventsViewSet
        assert resolver.func.actions == {
            "get": "retrieve",
            "head": "retrieve",
            "patch": "partial_update",
            "put": "update",
            "delete": "destroy",
        }

    def test_events_attendees_url(self):
        url = reverse("events:events-attendees", kwargs={"pk": 1})
        resolver = resolve(url)

        assert resolver.app_name == "events"
        assert resolver.view_name == "events:events-attendees"
        assert resolver.route == "^events/(?P<pk>[^/.]+)/attendees/$"
        assert resolver.func.cls == views.EventsViewSet
        assert resolver.func.actions == {"delete": "attendees", "post": "attendees"}
