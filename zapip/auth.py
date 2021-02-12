from functools import wraps
from typing import Any, Callable

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.http.request import HttpRequest


def valid_header_authentication(request: HttpRequest) -> bool:
    """
    Validates that all headers defined in settings.HEADER_AUTH are present
    and equal to the expected value.
    """
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
        return HttpResponseForbidden()
    return _wrapped_view
