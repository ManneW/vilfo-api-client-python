"""The exceptions used by the Vilfo client."""
class VilfoException(Exception):
    """General Vilfo exception occurred."""

class AuthenticationException(VilfoException):
    """An exception occurred related to authentication."""