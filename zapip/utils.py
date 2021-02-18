import logging
import uuid
from typing import Any

from django.http.response import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def valid_uuid(uuid_string: str) -> bool:
    """
    Verify that a string a valid UUID of any version, in standard form.
    """
    try:
        val = uuid.UUID(uuid_string)
    except ValueError:
        return False
    return uuid_string == str(val)


# If you have updated to Django 3.2 and see the custom response classes failing,
# change these to pass the headers to the parent init method.
# https://github.com/django/django/commit/bcc2befd0e9c1885e45b46d0b0bcdc11def8b249


class ZapipResponse(JsonResponse):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._headers["x-zapip-response-from"] = ("X-Zapip-Response-From", "zapip")


class ZapipResponseForbidden(ZapipResponse):
    status_code = 403


class ZoomResponse(HttpResponse):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._headers["x-zapip-response-from"] = ("X-Zapip-Response-From", "zoom")
