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


class ZapipResponse(JsonResponse):
    def __init__(self, **kwargs: Any):
        super().__init__(headers={"X-Zapip-Response-From": "zapip"}, **kwargs)


class ZapipResponseForbidden(ZapipResponse):
    status_code = 403


class ZoomResponse(HttpResponse):
    def __init__(self, **kwargs: Any):
        super().__init__(headers={"X-Zapip-Response-From": "zoom"}, **kwargs)
