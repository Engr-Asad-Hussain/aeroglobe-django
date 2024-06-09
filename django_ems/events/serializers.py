from rest_framework import serializers

from django_ems.events.models import Events
from django_ems.users_auth.serializers import UsersSerializer


class EventsSerializer(serializers.ModelSerializer):
    attendees = UsersSerializer(many=True, read_only=True)

    class Meta:
        model = Events
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "created_at",
            "updated_at",
            "attendees",
        )
        extra_kwargs = {
            "title": {"required": True},
            "description": {"required": True},
            "date": {"required": True},
            "location": {"required": True},
        }
