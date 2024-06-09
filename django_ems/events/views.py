from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django_ems.events.models import Events
from django_ems.events.serializers import EventsSerializer


class EventsViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all().order_by("id")
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: EventsSerializer):
        serializer.save(owner=self.request.user)
