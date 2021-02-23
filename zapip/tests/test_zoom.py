from django.test import TestCase
from django.test.utils import override_settings
from zapip.zoom import get_zoom_client


class ZoomClientTestCase(TestCase):
    def test_get_zoom_client(self):
        base_url = "https://zoom-test.example.com/"
        headers = {"foo": "bar"}
        with override_settings(ZOOM_API_BASE_URL=base_url, ZOOM_API_HEADERS=headers):
            client = get_zoom_client()
        self.assertEqual(client.url, base_url)
        self.assertEqual(client.headers, headers)
