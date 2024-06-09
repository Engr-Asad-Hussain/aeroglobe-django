from rest_framework import decorators, status, viewsets
from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.request import Request
from rest_framework.response import Response

from django_ems.events.models import Events
from django_ems.events.serializers import EventsPagination, EventsSerializer


class IsOwner(BasePermission):
    def has_object_permission(
        self, request: Request, view: "EventsViewSet", obj: Events
    ) -> bool:
        return True if request.method in SAFE_METHODS else request.user == obj.owner


class EventsViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all().order_by("id")
    serializer_class = EventsSerializer
    pagination_class = EventsPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwner]

    def perform_create(self, serializer: EventsSerializer):
        serializer.save(owner=self.request.user)

    @decorators.action(
        url_path="attendees",
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def attendees(self, request: Request, pk: int | None = None) -> Response:
        return {"POST": self._attend_events, "DELETE": self._drop_events}[
            request.method
        ](request, pk)

    def _attend_events(self, request: Request, pk: int | None = None) -> Response:
        event: Events = self.get_object()
        event.attendees.add(request.user)
        return Response(
            data={"detail": "You have been added to the event."},
            status=status.HTTP_201_CREATED,
        )

    def _drop_events(self, request: Request, pk: int | None = None) -> Response:
        event: Events = self.get_object()
        event.attendees.remove(request.user)
        return Response(
            data={"detail": "You have been removed from the event."},
            status=status.HTTP_200_OK,
        )
