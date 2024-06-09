from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django_ems.events.views import EventsViewSet

router = DefaultRouter()
router.register(r"events", EventsViewSet)

app_name = "events"
urlpatterns = [path("", include(router.urls))]
