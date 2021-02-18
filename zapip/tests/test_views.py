import uuid
from typing import Any
from urllib.parse import urljoin

import requests_mock
from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.test import Client, TestCase
from django.test.utils import override_settings
from zapip.models import ZoomMeeting


@override_settings(ZOOM_API_BASE_URL="https://zoom.example.com/")
class ZapipTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_id = "foo@example.com"
        self.meeting_id = 12340001234
        self.api_id = str(uuid.uuid4())
        self.application_id = str(uuid.uuid4())
        self.subscription_id = str(uuid.uuid4())

    def gateway_headers(self):
        return {
            "HTTP_X_API": self.api_id,
            "HTTP_X_API_APPLICATION": self.application_id,
            "HTTP_X_API_SUBSCRIPTION": self.subscription_id,
        }

    def zoom_url(self, path):
        return urljoin(settings.ZOOM_API_BASE_URL, path)

    def _create_meeting(self, mock: Any) -> HttpResponse:
        endpoint = self.zoom_url("/v2/users/{}/meetings".format(self.user_id))
        mock.post(
            endpoint,
            status_code=201,
            json={"id": self.meeting_id, "topic": "Test"},
            headers={
                "content-type": "application/json",
                "x-zoom-something": "something",
            },
        )
        response = self.client.post(
            "/zoom/v2/users/{}/meetings".format(self.user_id),
            data={"topic": "Test"},
            **self.gateway_headers()
        )
        return response


class CreateMeetingTestCase(ZapipTestCase):
    def test_requires_header_auth_if_enabled(self):
        self.client.headers = {"Authorization": "correct"}
        with self.settings(HEADER_AUTH={"Authorization": "correct"}):
            response = self.client.post("/zoom/v2/users/foo@example.com/meetings")
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["error"], "unauthenticated-proxy")

    def test_user_id_me_is_forbidden(self):
        response = self.client.post(
            "/zoom/v2/users/me/meetings", **self.gateway_headers()
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get("x-zapip-response-from"), "zapip")
        data = response.json()
        self.assertEqual(data["error"], "forbidden-user-id")

    @requests_mock.Mocker()
    def test_proxies_request_and_returns_content(self, mock: Any):
        response = self._create_meeting(mock)
        self.assertEqual(response["x-zapip-response-from"], "zoom")
        self.assertEqual(response["x-zoom-something"], "something")
        self.assertEqual(response.json()["id"], self.meeting_id)
        self.assertEqual(response.json()["topic"], "Test")

    @requests_mock.Mocker()
    def test_saves_meeting_id_for_proxied_requests(self, mock: Any):
        self._create_meeting(mock)
        meeting = ZoomMeeting.objects.filter(
            application__external_id=self.application_id,
            meeting_id=self.meeting_id,
            user_id=self.user_id,
        )
        self.assertTrue(meeting.exists())


class ReadUpdateDeleteMeetingTestCase(ZapipTestCase):
    @requests_mock.Mocker()
    def test_get_method_denies_if_meeting_id_not_associated_with_application(
        self, mock: Any
    ):
        response = self.client.get(
            "/zoom/v2/meetings/{}".format(self.meeting_id), **self.gateway_headers()
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get("x-zapip-response-from"), "zapip")
        data = response.json()
        self.assertEqual(data["error"], "unknown-meeting-id")

    @requests_mock.Mocker()
    def test_get_method_allows_if_meeting_id_is_associated_with_application(
        self, mock: Any
    ):
        self._create_meeting(mock)
        endpoint = self.zoom_url("/v2/meetings/{}".format(self.meeting_id))
        mock.get(
            endpoint,
            json={"id": self.meeting_id, "topic": "Interesting stuff"},
            headers={
                "content-type": "application/json",
            },
        )
        response = self.client.get(
            "/zoom/v2/meetings/{}".format(self.meeting_id), **self.gateway_headers()
        )
        self.assertEqual(response["x-zapip-response-from"], "zoom")
        self.assertEqual(response.json()["id"], self.meeting_id)
        self.assertEqual(response.json()["topic"], "Interesting stuff")

    @requests_mock.Mocker()
    def test_proxies_query_params(self, mock: Any):
        self._create_meeting(mock)
        endpoint = self.zoom_url(
            "/v2/meetings/{}{}".format(
                self.meeting_id, "?schedule_for_reminder=false&boo=true"
            )
        )
        mock.get(
            endpoint,
            json={"id": self.meeting_id, "topic": "Coffee"},
            headers={
                "content-type": "application/json",
            },
        )
        response = self.client.get(
            "/zoom/v2/meetings/{}".format(self.meeting_id),
            {"schedule_for_reminder": "false",
            "boo": "true"},
            **self.gateway_headers()
        )
        self.assertEqual(mock.last_request.qs, {"schedule_for_reminder": ["false"], "boo": ["true"]})
