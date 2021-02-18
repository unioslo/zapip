import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_zoom_client(
    url: Optional[str] = None, headers: Optional[Dict[str, str]] = None
) -> "ZoomClient":
    """
    Initializes a ZoomClient according to app settings.
    """
    default_headers = settings.ZOOM_API_HEADERS
    headers = headers or {}
    headers.update(default_headers)
    return ZoomClient(
        url=url or settings.ZOOM_API_BASE_URL,
        headers=headers,
    )


class ZoomClient:
    """
    A very simple Zoom client, mostly a wrapper around requests.
    """

    def __init__(self, url: str, headers: Optional[Dict[str, str]]):
        self.url = url
        self.headers = {} if headers is None else headers
        self.session = requests.Session()

    def _build_request_headers(
        self, headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        request_headers = {}
        for h in self.headers:
            request_headers[h] = self.headers[h]
        for h in headers or ():
            request_headers[h] = headers[h]
        return request_headers

    def call(
        self,
        method_name: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.models.Response:
        headers = self._build_request_headers(headers)
        logger.debug(
            "Calling %s %s with params=%r", method_name, urlparse(url).path, params
        )
        return self.session.request(
            method_name, url, headers=headers, params=params, **kwargs
        )

    def get(self, url: str, **kwargs):
        return self.call("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.call("POST", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.call("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.call("DELETE", url, **kwargs)

    def create_meeting(self, user_id: str, data: Any, **kwargs: Any):
        return self.post(
            urljoin(self.url, f"v2/users/{user_id}/meetings"), data=data, **kwargs
        )

    def get_meeting(self, meeting_id: int, data: Any, **kwargs: Any):
        return self.get(
            urljoin(self.url, f"v2/meetings/{meeting_id}"), data=data, **kwargs
        )

    def update_meeting(self, meeting_id: int, data: Any, **kwargs: Any):
        return self.patch(
            urljoin(self.url, f"v2/meetings/{meeting_id}"), data=data, **kwargs
        )

    def delete_meeting(self, meeting_id: int, data: Any, **kwargs: Any):
        return self.delete(
            urljoin(self.url, f"v2/meetings/{meeting_id}"), data=data, **kwargs
        )
