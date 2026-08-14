"""DRF JWT authentication class."""
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api.auth.jwt_utils import decode_token

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """Authenticate requests using Bearer JWT access tokens."""

    www_authenticate_header = 'Bearer'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]
        payload = decode_token(token)
        if payload is None:
            raise AuthenticationFailed('Could not validate credentials')

        if payload.get('type') != 'access':
            raise AuthenticationFailed('Could not validate credentials')

        username = payload.get('sub')
        if not username:
            raise AuthenticationFailed('Could not validate credentials')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed('Could not validate credentials')

        if not user.is_active:
            raise AuthenticationFailed('User account is inactive')

        return (user, token)

    def authenticate_header(self, request):
        return self.www_authenticate_header
