import logging
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.utils.decorators import method_decorator
from django.views import View
from requests.models import Response

from zapip.auth import (
    gateway_headers_required,
    get_gateway_headers,
    header_auth_required,
)
from zapip.models import Application, ZoomMeeting
from zapip.utils import ZapipResponseForbidden, ZoomResponse
from zapip.zoom import get_zoom_client

logger = logging.getLogger(__name__)

auth_decorators = [header_auth_required, gateway_headers_required]


EXCLUDED_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-encoding",
    "content-length",
}


def proxy_zoom_response(zoom_response: Response) -> ZoomResponse:
    # pass content and status codes as-is
    response = ZoomResponse(
        content=zoom_response.content,
        status=zoom_response.status_code,
    )
    # exclude certain headers
    for header, value in zoom_response.headers.items():
        if header.lower() in EXCLUDED_HEADERS:
            continue
        response[header] = value
    return response


@method_decorator(auth_decorators, name="dispatch")
class CreateMeeting(View):
    """
    Create a meeting for a user.

    Proxies the request and saves the user_id, meeting_id and application.
    """

    def post(self, request: HttpRequest, user_id: str):
        """
        POST /users/{userId}/meetings
        https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingcreate
        """
        if user_id == "me":
            return ZapipResponseForbidden(
                data={
                    "error": "forbidden-user-id",
                    "detail": "user_id path argument cannot be 'me'",
                }
            )
        application, _ = Application.objects.get_or_create(
            external_id=request.gateway_headers["application"]
        )
        logger.info(
            "Forwarding POST to /users/%s/meetings for application=%r",
            user_id,
            application,
        )
        zoom = get_zoom_client()
        zoom_response = zoom.create_meeting(user_id=user_id, data=request.body)
        if zoom_response.status_code == 200:
            zoom_data = zoom_response.json()
            meeting_id = zoom_data.get("id")
            meeting = ZoomMeeting.objects.create(
                user_id=user_id,
                meeting_id=meeting_id,
                application=application,
            )
            logger.info("Saved %r", meeting)
        response = proxy_zoom_response(zoom_response)
        return response


@method_decorator(auth_decorators, name="dispatch")
class ReadUpdateDeleteMeeting(View):
    """
    Read, update and delete meetings.

    Proxies the request if the meeting_id is associated with the requesting application.
    """

    http_method_names = ["get", "patch", "delete"]

    def _lookup_meeting_and_application(
        self, request: HttpRequest, meeting_id: int
    ) -> Tuple[ZoomMeeting, Application]:

        return meeting, application, error

    def dispatch(self, request: HttpRequest, meeting_id: int):
        """
        GET /meetings/{meetingId}
        https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meeting

        PATCH /meetings/{meetingId}
        https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingupdate

        DELETE /meetings/{meetingId}
        https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingdelete
        """
        application, _ = Application.objects.get_or_create(
            external_id=request.gateway_headers["application"]
        )
        meeting = ZoomMeeting.objects.filter(
            application=application, meeting_id=meeting_id
        ).first()
        if not meeting:
            return ZapipResponseForbidden(
                data={
                    "error": "unknown-meeting-id",
                    "detail": "meeting id is not known to the proxy or not associated with your application",
                }
            )
        logger.info(
            "Forwarding %s to /meetings/%s for application=%r",
            request.method,
            meeting_id,
            application,
        )
        zoom = get_zoom_client()
        method_handlers = {
            "GET": zoom.get_meeting,
            "PATCH": zoom.update_meeting,
            "DELETE": zoom.delete_meeting,
        }
        handler = method_handlers[request.method]
        zoom_response = handler(meeting_id=meeting_id, data=request.body)
        response = proxy_zoom_response(zoom_response)
        return response
