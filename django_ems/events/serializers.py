from rest_framework import pagination, serializers
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnList

from django_ems.events.models import Events
from django_ems.users_auth.serializers import UsersSerializer


class EventsPagination(pagination.PageNumberPagination):
    page_size = 3
    page_query_param = "page"
    max_page_size = 10

    def get_paginated_response(self, data: ReturnList) -> Response:
        return Response(
            {
                "page": self.page.number,
                "page_size": self.page_size,
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


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
