from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.http.request import HttpRequest

from zapip.auth import header_auth_required


@header_auth_required
def restricted_view(request) -> HttpResponse:
    return HttpResponse()


class HeaderAuthTestCase(TestCase):
    def setUp(self):
        self.request: HttpRequest = RequestFactory().get('/restricted')

    def test_allows_valid_header(self):
        self.request.headers = {
            'Authorization': 'correct'
        }
        with self.settings(HEADER_AUTH={'Authorization': 'correct'}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_allows_multiple_valid_Headers(self):
        self.request.headers = {
            'Authorization': 'correct',
            'Foo': 'also correct'
        }
        with self.settings(HEADER_AUTH={'Authorization': 'correct',
                                              'Foo': 'also correct'}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_denies_invalid_header(self):
        self.request.headers = {
            'Authorization': 'wrong'
        }
        with self.settings(HEADER_AUTH={'Authorization': 'correct'}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_denies_one_invalid_header_of_multiple(self):
        self.request.headers = {
            'Authorization': 'correct',
            'Foo': 'correct'
        }
        with self.settings(HEADER_AUTH={'Authorization': 'correct',
                                              'Foo': 'wrong'}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_denies_missing_header(self):
        with self.settings(HEADER_AUTH={'Authorization': 'correct'}):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 403)

    def test_disabled_if_not_configured(self):
        with self.settings(HEADER_AUTH=None):
            response = restricted_view(self.request)
        self.assertEqual(response.status_code, 200)
