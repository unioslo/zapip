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
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64)
    # subscriptions = models.ManyToManyField(
    #     'Subscription', through='ApplicationSubscription', related_name='applications')

    # def __str__(self):
    #     return str(self.uid)

    def __repr__(self):
        return "{}(name={!r}, slug={!r})".format(
            self.__class__.__name__,
            self.name,
            self.slug)


class Subscription(BaseModel):
    """
    An API subscription
    """
    application = models.ForeignKey('Application', on_delete=models.PROTECT)
    gateway_id = models.CharField(max_length=32)

    def __repr__(self):
        return "{}(name={!r}, slug={!r})".format(
            self.__class__.__name__,
            self.application,
            self.gateway_id)
