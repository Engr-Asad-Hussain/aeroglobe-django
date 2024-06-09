from django.contrib import admin

from django_ems.events.models import Events


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "date", "location", "owner")
    search_fields = ("title", "owner__email")
    ordering = ["id"]
    readonly_fields = ("created_at", "updated_at")
    fields = ("title", "description", "date", "location", "owner", "attendees")
    filter_horizontal = ("attendees",)
