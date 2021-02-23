import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.http.request import HttpRequest

from zapip.utils import ZapipResponseForbidden, valid_uuid

logger = logging.getLogger(__name__)


def valid_header_authentication(request: HttpRequest) -> bool:
    """
    Validates that all headers defined in settings.HEADER_AUTH are present
    and equal to the expected value.
    """
    if not hasattr(settings, "HEADER_AUTH"):
        raise ImproperlyConfigured("HEADER_AUTH is not set")
    if settings.HEADER_AUTH is None:
        return True
    for name, value in settings.HEADER_AUTH.items():
        if request.headers.get(name) != value:
            return False
    return True


def header_auth_required(view_func: Callable[[HttpRequest], HttpResponse]):
    """
    Wraps a view and denies requests where the headers don't validate.
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if valid_header_authentication(request):
            return view_func(request, *args, **kwargs)
        return ZapipResponseForbidden(
            data={
                "error": "unauthenticated-proxy",
            }
        )

    return _wrapped_view


def get_gateway_headers(request: HttpRequest) -> Dict[str, Optional[str]]:
    wanted_headers = {
        "api": settings.GATEWAY_API_ID_HEADER,
        "application": settings.GATEWAY_APPLICATION_ID_HEADER,
        "subscription": settings.GATEWAY_SUBSCRIPTION_ID_HEADER,
    }
    return {
        name: request.headers.get(header) for name, header in wanted_headers.items()
    }


def valid_gateway_headers(headers: Dict[str, Optional[str]]) -> bool:
    """
    Validates that headers expected to be set by the API gateway are set.

    The required headers are defined on the following settings:
      - GATEWAY_API_ID_HEADER
      - GATEWAY_APPLICATION_ID_HEADER
      - GATEWAY_SUBSCRIPTION_ID_HEADER
    """
    return all(
        [(isinstance(value, str) and valid_uuid(value)) for value in headers.values()]
    )


def gateway_headers_required(view_func: Callable[[HttpRequest], HttpResponse]):
    """
    Wraps a view and denies requests where expected gateway headers are missing.
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        gateway_headers = get_gateway_headers(request)
        if valid_gateway_headers(gateway_headers):
            logger.info("Request accepted with gateway headers %r", gateway_headers)
            request.gateway_headers = gateway_headers
            return view_func(request, *args, **kwargs)
        logger.info("Request denied with gateway headers %r", gateway_headers)
        return ZapipResponseForbidden(
            data={
                "error": "missing-headers",
            }
        )

    return _wrapped_view
