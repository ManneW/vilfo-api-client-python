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
