import uuid

from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.test import RequestFactory, TestCase
from zapip.auth import (
    gateway_headers_required,
    get_gateway_headers,
    header_auth_required,
)


@header_auth_required
def restricted_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse()


@gateway_headers_required
def gateway_header_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse()


class HeaderAuthTestCase(TestCase):
    def setUp(self):
        self.request: HttpRequest = RequestFactory().get("/restricted")

    def test_allows_valid_header(self):
        self.request.headers = {"Authorization": "correct"}
        with self.settings(HEADER_AUTH={"Authorization": "correct"}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_allows_multiple_valid_Headers(self):
        self.request.headers = {"Authorization": "correct", "Foo": "also correct"}
        with self.settings(
            HEADER_AUTH={"Authorization": "correct", "Foo": "also correct"}
        ):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_denies_invalid_header(self):
        self.request.headers = {"Authorization": "wrong"}
        with self.settings(HEADER_AUTH={"Authorization": "correct"}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_denies_one_invalid_header_of_multiple(self):
        self.request.headers = {"Authorization": "correct", "Foo": "correct"}
        with self.settings(HEADER_AUTH={"Authorization": "correct", "Foo": "wrong"}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_denies_missing_header(self):
        with self.settings(HEADER_AUTH={"Authorization": "correct"}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_disabled_if_not_configured(self):
        with self.settings(HEADER_AUTH=None):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_sets_headers_and_data_on_denial(self):
        with self.settings(HEADER_AUTH={"Authorization": "correct"}):
            response = restricted_view(self.request)
        self.assertEqual(response.get("x-zapip-response-from"), "zapip")
        self.assertEqual(response.content, b'{"error": "unauthenticated-proxy"}')


class GatewayHeaderTestCase(TestCase):
    def setUp(self):
        self.request: HttpRequest = RequestFactory().get("/needs-gateway-headers")
        self.uuid_one = str(uuid.uuid4())
        self.uuid_two = str(uuid.uuid4())
        self.uuid_three = str(uuid.uuid4())

    def set_expected_headers(self):
        self.request.headers = {
            settings.GATEWAY_API_ID_HEADER: self.uuid_one,
            settings.GATEWAY_APPLICATION_ID_HEADER: self.uuid_two,
            settings.GATEWAY_SUBSCRIPTION_ID_HEADER: self.uuid_three,
        }

    def test_allows_when_all_headers_are_present(self):
        self.set_expected_headers()
        response = gateway_header_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_denies_when_headers_missing(self):
        response = gateway_header_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_denies_if_one_header_is_missing(self):
        self.request.headers = {
            settings.GATEWAY_API_ID_HEADER: self.uuid_one,
            settings.GATEWAY_SUBSCRIPTION_ID_HEADER: self.uuid_three,
        }
        response = gateway_header_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_denies_if_a_header_is_not_an_uuid(self):
        self.request.headers = {
            settings.GATEWAY_API_ID_HEADER: self.uuid_one,
            settings.GATEWAY_APPLICATION_ID_HEADER: "What did 0 say to 1?  You're a bit too much.",
            settings.GATEWAY_SUBSCRIPTION_ID_HEADER: self.uuid_three,
        }
        response = gateway_header_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_get_gateway_headers(self):
        self.set_expected_headers()
        headers = get_gateway_headers(self.request)
        self.assertEqual(headers["api"], self.uuid_one)
        self.assertEqual(headers["application"], self.uuid_two)
        self.assertEqual(headers["subscription"], self.uuid_three)

    def test_sets_headers_and_data_on_denial(self):
        response = gateway_header_view(self.request)
        self.assertEqual(response.get("x-zapip-response-from"), "zapip")
        self.assertEqual(response.content, b'{"error": "missing-headers"}')
