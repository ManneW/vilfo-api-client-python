# vilfo-api-client-python

This is the initial version of a python module and API client for the Vilfo router. The module is targeted towards compatibility with Python3.

Currently, the client is quite limited but will be extended with support for additional endpoints over time.

See `vilfo/client.py` for additional information about available methods. A short usage example is available in this README as well.

## Legal Disclaimer

Please note that this software is not affiliated with Vilfo AB, is not an official client for the Vilfo router API and the developers take no legal responsibility for the functionality or security of your Vilfo router. Support is only offered on a community basis.

## Information about the Vilfo router and API

You can find more information about the Vilfo router on [www.vilfo.com](https://www.vilfo.com/).

From there you can also find information about the API in the form of the official API documentation: https://www.vilfo.com/apidocs/

## Installation

The preferred installation method is by using `pip`:

`pip install vilfo-api-client`

## Usage

The API client is available through the class `vilfo.Client`. To establish a connection and make the API calls, you will need the **hostname or IP of your router** (`admin.vilfo.com` is the default one) as well as an **API access token**.

### Obtaining an access token

Information about how to get an access token is described in the official API documentation: https://www.vilfo.com/apidocs/#header-authorization

**Note:** In version 1.0.13 of the Vilfo firmware, access tokens are invalidated when a new login to the web UI is made. To prevent web UI logins from interfering with the API calls, you can create a separate user solely for API purposes and use its access token.

### Creating the client and making calls

This is a basic sample of how you can use the `vilfo-api-client`.

```python
import vilfo

client = vilfo.Client(
    host='admin.vilfo.com',
    token='YOUR_ACCESS_TOKEN'
)

# Ping to check if router is online
result = client.ping()
print(result)

try:
    # Get the last reported load
    result = client.get_load()
    print(result)

    # Get a list of all devices
    result = client.get_devices()
    print(result)

    # Get a boolean indicating if a device is online or not
    result = client.is_device_online(
        mac_address='08:00:27:8e:ac:31'
    )
    print(result)

    # Get detailed information about a specific device
    result = client.get_device(
        mac_address='08:00:27:8e:ac:31'
    )
    print(result)

except vilfo.exceptions.AuthenticationException:
    print("Authentication Exception")
```

### Exceptions and error handling

The `vilfo-api-client` library defines a set of exceptions that can be used to handle errors. These exception classes are located under `vilfo.exceptions`.

*Additional information about the exceptions will be added and exception and error handling will be improved further.*

## Changelog

### Version 0.3.1

Minor adjustment in Client constructor to allow for better mocking during testing.

### Version 0.3

Initial stable release.