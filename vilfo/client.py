'''
Client for communicating with Vilfo API
'''
import json
import requests

import vilfo.exceptions


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
        """Internal method to facilitate performing requests with authentication added to them
        and appropriate creation of common exceptions if they are encountered.
        """
        url = self._base_url + endpoint
        headers = headers or {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % self._token,
        }
        timeout = timeout or self.DEFAULT_TIMEOUT

        try:
            response = getattr(requests, method)(url, headers=headers, data=data, params=params, timeout=timeout)
        except requests.exceptions.RequestException as ex:
            raise ex

        if 404 == response.status_code:
            raise vilfo.exceptions.VilfoException()

        if 403 == response.status_code or response_content_is_login_page(response.content):
            raise vilfo.exceptions.AuthenticationException()

        return response

    def ping(self):
        """Perform a check if the Vilfo router is online.

        See https://www.vilfo.com/apidocs/#system-ping-get for more information.

        Note that this endpoint can be called and executed successfully even when not providing
        valid credentials.
        """
        response = None
        try:
            response = self._request('get', '/system/ping')
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def get_devices(self):
        """Get a list of all devices connected to the router.

        See https://www.vilfo.com/apidocs/#devices-devices-get for more information.
        """
        response = None
        try:
            response = self._request('get', '/devices')
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def get_device(self, mac_address):
        """Get information about a specific device by MAC address.

        See https://www.vilfo.com/apidocs/#devices-devices-get-1 for more information.
        """
        response = None
        try:
            response = self._request('get', '/devices/%s' % mac_address)
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def is_device_online(self, mac_address):
        """Returns a boolean indicating whether or not the device is online.

        Uses the get_device method under the hood.
        """
        try:
            result = self.get_device(mac_address)

            return result['data']['status']['online']
        except:
            return False

        return False

    def get_board_information(self):
        """Return information about system.

        For more information:
            * https://www.vilfo.com/apidocs/#dashboard-board-information-get
        """
        response = None

        try:
            response = self._request('get', '/dashboard/board')
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def get_load(self):
        """Get the current load in percent.

        Note: This is currently implemented as first trying to fetch the load from get_board_information,
              but since is not seems to always be present there, falls back to extract it from get_utilization.

        For more information:
            * https://www.vilfo.com/apidocs/#dashboard-board-information-get
            * https://www.vilfo.com/apidocs/#dashboard-utilization-get
        """
        try:
            result = self.get_board_information()
            if "load" in result:
                return result['load']
        except:
            raise

        try:
            result = self.get_utilization()
            if "utilization" in result and len(result["utilization"]) > 0:
                return result['utilization'][-1]
        except:
            return None

    def get_utilization(self):
        """Return timeseries information about utilization for recent 3 hours.

        See https://www.vilfo.com/apidocs/#dashboard-utilization-get for more information.
        """
        response = None
        try:
            response = self._request('get', '/dashboard/utilization')
        except:
            raise

        return json.loads(response.text)

    def get_online_devices(self):
        """Return information about online vs. offline devices.

        See https://www.vilfo.com/apidocs/#dashboard-online-devices-get for more information.
        """
        response = None
        try:
            response = self._request('get', '/dashboard/online-devices')
        except:
            raise

        return json.loads(response.text)

    def reboot_router(self):
        """Perform a reboot of the router.

        Tip: To detect when the router is back online, use the ping() method.

        For more information:
            * https://www.vilfo.com/apidocs/#system-reboot-post
        """
        response = None
        try:
            response = requests.post(
                self._base_url + '/system/reboot'
            )
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)


# Utility methods
def response_content_is_login_page(response_content):
    """Returns True if the provided response_content seems to be from the Vilfo login page."""

    detectors = [
        "<title>Login | Vilfo</title>",
        "<Login-Form",
    ]

    detected_count = 0

    for detector in detectors:
        if detector in str(response_content):
            detected_count += 1

    return (detected_count >= (len(detectors) / 2))  # Allow half of the detectors to fail for now.
