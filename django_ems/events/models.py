from django.db import models
from django.utils import timezone


class Events(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    date = models.DateField(null=True)
    location = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE)
    attendees = models.ManyToManyField("users.User", related_name="events_attended")
