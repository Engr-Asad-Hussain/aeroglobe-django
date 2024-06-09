from rest_framework import viewsets
from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.request import Request

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
