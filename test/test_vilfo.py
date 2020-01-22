import unittest
import vilfo
import responses

class TestVilfo(unittest.TestCase):
    @responses.activate
    def test_ping(self):
        """
        Test that ping is working as expected
        """
        client = vilfo.Client('vilfotestrouter', 'testtoken')

        responses.add(responses.GET, 'http://vilfotestrouter/api/v1/system/ping',
                      json={'message': 'Online'}, status=200)
        
        resp = client.ping()

        self.assertEqual(resp, {'message': 'Online'})

    @responses.activate
    def test_get_device(self):
        """
        Test that the fetching of devices triggers a call to the appropriate endpoint
        """
        client = vilfo.Client('vilfotestrouter', 'testtoken')

        responses.add(responses.GET, 'http://vilfotestrouter/api/v1/devices/abc:123',
                      json={
                        "data": {
                            "blocked": False,
                            "hostname": "box-7",
                            "displayName": "Box 7",
                            "ipv4": "192.168.0.7",
                            "mac_address": "08:00:27:8e:ac:31",
                            "vendor": "PCS Systemtechnik GmbH",
                            "vilfo_group": 1,
                            "bandwidth": {
                            "download": 0.5,
                            "upload": 0.2,
                            "total": 0.7
                            },
                            "bypass": True,
                            "first_seen_at": "2017-09-20T12:42:58+00:00",
                            "status": {
                            "online": True,
                            "online_from": "2017-09-20T12:42:58+00:00"
                            }
                        }
                      }, status=200)
        
        resp = client.get_device('abc:123')

        self.assertIsNotNone(resp)

    @responses.activate
    def test_is_device_online(self):
        """
        Test that it works as expected to check if a device is online
        """
        client = vilfo.Client('vilfotestrouter', 'testtoken')
        mac_address = 'abc:123'

        # Device that is supposed to exist and is online
        responses.add(responses.GET, 'http://vilfotestrouter/api/v1/devices/abc:123', json={'data': {'status': {'online': True}}})
        # Device that is supposed to exist and is offline
        responses.add(responses.GET, 'http://vilfotestrouter/api/v1/devices/abc:123', json={'data': {'status': {'online': False}}})
        # Device that is not found
        responses.add(responses.GET, 'http://vilfotestrouter/api/v1/devices/abc:123', status=404)
        # Incomplete response data
        responses.add(responses.GET, 'http://vilfotestrouter/api/v1/devices/abc:123', json={'data': 'incomplete'})

        resp = client.is_device_online(mac_address)
        self.assertTrue(resp)
        resp = client.is_device_online(mac_address)
        self.assertFalse(resp)
        resp = client.is_device_online(mac_address)
        self.assertFalse(resp)
        resp = client.is_device_online(mac_address)
        self.assertFalse(resp)
