from django.db import models
from django.db.models import Lookup
from django.db.models.fields import Field


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Application(BaseModel):
    """
    An application
    """

    name = models.CharField(max_length=64, blank=True, null=True)
    external_id = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return "{}(name={!r}, external_id={!r})".format(
            self.__class__.__name__, self.name, self.external_id
        )


class ZoomMeeting(BaseModel):
    application = models.ForeignKey("Application", on_delete=models.PROTECT)
    user_id = models.CharField(max_length=128)
    meeting_id = models.BigIntegerField()

    def __str__(self):
        return "{} ({})".format(self.user_id, self.meeting_id)

    def __repr__(self):
        return "{}(pk={!r}, user_id={!r}, meeting_id={!r}, application={!r})".format(
            self.__class__.__name__,
            self.pk,
            self.user_id,
            self.meeting_id,
            self.application,
        )
