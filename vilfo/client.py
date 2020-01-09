'''
Client for communicating with Vilfo API
'''

import json
import requests


class Client:
    """
    Vilfo API client
    """
    DEFAULT_TIMEOUT = 20

    def __init__(self, host, token, ssl=False):

        self._host = host
        self._token = token
        protocol = 'https://' if ssl else 'http://'
        self._base_url = protocol + host + '/api/v1'

    def _request(self, method, endpoint, headers=None, data=None, params=None, timeout=None):
        url = self._base_url + endpoint
        headers = headers or {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % self._token,
        }
        timeout = timeout or self.DEFAULT_TIMEOUT

        response = getattr(requests, method)(url, headers=headers, data=data, params=params, timeout=timeout)

        return response

    def ping(self):
        response = None
        try:
            response = self._request('get', '/system/ping')
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def get_devices(self):
        response = None
        try:
            response = self._request('get', '/devices')
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def get_device(self, mac_address):
        response = None
        try:
            response = requests.get(
                self._base_url + '/devices/' + mac_address,
                headers={
                    'Authorization': 'Bearer ' + self._token })
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def is_device_online(self, mac_address):
        response = None

        try:
            response = requests.get(
                self._base_url + '/devices/' + mac_address,
                headers={
                    'Authorization': 'Bearer ' + self._token })
        except requests.exceptions.RequestException as ex:
            raise ex

        try:
            result = json.loads(response.text)
            
            return result['data']['status']['online']
        except:
            return False

        return False

    def reboot_router(self):
        response = None
        try:
            response = requests.post(
                self._base_url + '/system/reboot'
            )
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)