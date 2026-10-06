"""Game-authenticated ad gateway settings and server-to-server contracts."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, override_settings

from game import ad_gateway


class AdGatewayTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get('/api/ads/decision/', {'slot_id': 'village-board'})
        self.request.user = SimpleNamespace(is_authenticated=True)
        self.player = SimpleNamespace(pk=7, room_id='room-01', coins=12, version=3)

    def test_game_settings_load_media_configuration(self):
        for name in ('ADS_BASE_URL', 'ADS_MEDIA_ID', 'ADS_MEDIA_KEY'):
            with self.subTest(name=name):
                self.assertTrue(getattr(settings, name))

    @override_settings(ADS_BASE_URL='http://127.0.0.1:8001',
                       ADS_MEDIA_ID='village-game', ADS_MEDIA_KEY='test-media-key')
    def test_authenticated_decision_proxies_public_context_with_server_key(self):
        upstream = MagicMock()
        upstream.status = 200
        upstream.read.return_value = b'{"empty": true, "slot_id": "village-board"}'
        with patch.object(ad_gateway.Player.objects, 'get', return_value=self.player), \
                patch.object(ad_gateway, 'urlopen') as open_url:
            open_url.return_value.__enter__.return_value = upstream
            response = ad_gateway.decision(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['empty'])
        self.assertEqual(response['Cache-Control'], 'no-store')
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, 'http://127.0.0.1:8001/api/media/decision/')
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.get_header('X-media-key'), 'test-media-key')
        self.assertIsNone(request.get_header('Cookie'))
        body = json.loads(request.data)
        self.assertEqual(body['subject'], {'media_id': 'village-game', 'subject_id': '7'})
        self.assertEqual(body['slot_id'], 'village-board')
        self.assertEqual(body['context']['coins'], 12)
        self.assertEqual(open_url.call_args.kwargs['timeout'], 3)

    def test_unauthenticated_viewer_never_calls_ads(self):
        self.request.user.is_authenticated = False
        with patch.object(ad_gateway, 'call_ads') as call_ads:
            response = ad_gateway.decision(self.request)
        self.assertEqual(response.status_code, 401)
        call_ads.assert_not_called()

    @override_settings(ADS_BASE_URL='http://127.0.0.1:8001',
                       ADS_MEDIA_ID='village-game', ADS_MEDIA_KEY='test-media-key')
    def test_unreachable_ads_returns_503(self):
        from urllib.error import URLError
        with patch.object(ad_gateway.Player.objects, 'get', return_value=self.player), \
                patch.object(ad_gateway, 'urlopen', side_effect=URLError('offline')):
            response = ad_gateway.decision(self.request)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(json.loads(response.content), {'error': 'ads_unavailable'})
