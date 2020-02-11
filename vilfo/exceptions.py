"""The exceptions used by the Vilfo client."""
from requests.exceptions import RequestException

class VilfoException(Exception):
    """General Vilfo exception occurred."""

class AuthenticationException(VilfoException):
    """An exception occurred related to authentication."""

class NotFoundException(VilfoException):
    """An exception indicating an API resource was not found."""

class VilfoRequestException(VilfoException, RequestException):
    """An exception caught by Vilfo but raised by the requests library."""