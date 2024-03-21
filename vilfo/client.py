'''
Client for communicating with Vilfo API
'''
import ipaddress
import json
import requests
from semver import Version as Version

import vilfo.exceptions

from getmac import get_mac_address

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

        # MAC address not resolved yet
        self.mac = None
        self._mac_resolution_failed = False
        self._cached_mac = None
        self._firmware_version = "1.1.0"

        try:
            self._firmware_version = self.resolve_firmware_version()
        except vilfo.exceptions.VilfoException:
            pass

        try:
            self.mac = self.resolve_mac_address()
        except vilfo.exceptions.VilfoException:
            pass

        self._api_v1_supported = Version(self._firmware_version).compare("1.1.0") >= 0

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
            # Wrap the exception in our own exception class.
            raise vilfo.exceptions.VilfoRequestException(ex)

        if 404 == response.status_code:
            raise vilfo.exceptions.NotFoundException()

        if 403 == response.status_code or response_content_is_login_page(response.content):
            raise vilfo.exceptions.AuthenticationException()

        return response

    def resolve_firmware_version(self):
        """Try to resolve the current firmware version."""
        response = None
        try:
            response = self.get_board_information()
        except requests.exceptions.RequestException as ex:
            raise ex

        return response["version"]

    def resolve_mac_address(self, force_retry=False):
        """Try to resolve the MAC address for the router itself.
        
        The address is saved in the client instance, but by using force_retry.

        Raises:
            - vilfo.exception.VilfoException: if the resolution failed
        """
        if (self._cached_mac or self._mac_resolution_failed) and not force_retry:
            return self._cached_mac

        resolved_mac = None
        host_is_hostname = False
        valid_ipaddress = None
        ipaddress_version = None

        try:
            valid_ipaddress = ipaddress.ip_address(self._host)
            ipaddress_version = valid_ipaddress.version
        except ValueError:
            # For now, assume that the _host is a hostname if it's not a valid IP
            host_is_hostname = True

        try:
            if host_is_hostname:
                resolved_mac = get_mac_address(hostname=self._host, network_request=True)
            elif valid_ipaddress and ipaddress_version == 4:
                resolved_mac = get_mac_address(ip=self._host)
            elif valid_ipaddress and ipaddress_version == 6:
                resolved_mac = get_mac_address(ip6=self._host)
        except:
            pass

        if not resolved_mac:
            self._mac_resolution_failed = True
            raise vilfo.exceptions.VilfoException

        self._mac_resolution_failed = False
        self._cached_mac = resolved_mac

        return resolved_mac

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

    def get_device_by_ip(self, ip_address):
        """Get information about a specific device by IP address."""
        """Get information about a specific device by MAC address.

        See https://www.vilfo.com/apidocs/#devices-devices-get-1 for more information.
        """
        response = None
        try:
            response = self._request('get', '/devices/%s' % ip_address)
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def _get_device_by_mac(self, mac_address):
        response = None
        try:
            response = self._request('get', '/devices/%s' % mac_address)
        except requests.exceptions.RequestException as ex:
            raise ex

        return json.loads(response.text)

    def get_device(self, mac_address):
        """Get information about a specific device by MAC address.

        See https://www.vilfo.com/apidocs/#devices-devices-get-1 for more information.
        """
        if not self._api_v1_supported:
            """Use legacy version which fetches devices by MAC address"""
            return self._get_device_by_mac(mac_address)

        devices = None
        try:
            devices = self.get_devices()
        except requests.exceptions.RequestException as ex:
            raise ex

        try:
            device_info = list(filter(lambda device: device['mac_address'] and device['mac_address'] == mac_address, devices['data']))
        except Exception as ex:
            device_info = None

        device_current_ip = (device_info.pop())['ipv4']

        if not device_current_ip:
            return None

        return self.get_device_by_ip(device_current_ip)

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
