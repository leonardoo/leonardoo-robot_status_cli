import json

from rest_framework.authentication import (BasicAuthentication, get_authorization_header)
from rest_framework.exceptions import AuthenticationFailed

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class KeyFinder(object):

    Model = None
    queryset = None
    public_key_field = None
    user_field = None

    def get_queryset(self):
        qs = self.queryset
        if not qs:
            qs = self.Model.objects.all()
        return qs

    def get_key(self, public_key):
        qs = self.get_queryset()
        qs = qs.filter(**{
            self.public_key_field: public_key
        })
        if not qs.exists():
            raise AuthenticationFailed('Token invalid')
        key = qs[0]
        if not key.is_active:
            raise AuthenticationFailed('Token inactive or deleted')
        return key

    def verify(self, project_key, data, key):
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=project_key.secret_key.encode(),
            iterations=100000,
            backend=backend
        )
        try:

            kdf.verify(data.encode(), bytes.fromhex(key))
        except:
            raise AuthenticationFailed('Authentication failed')
        return

    def data_as_string(self, data):
        return json.dumps(data)

    def get_user(self, key):
        if not self.user_field:
            raise Exception("User need to be configurated")
        location = self.user_field.split("__")
        root = key
        for field in location:
            root = getattr(root, field)
        return root


class TokenAuthentication(KeyFinder, BasicAuthentication):

    def authenticate_header(self, request):
        return 'xBasic realm="%s"' % self.www_authenticate_realm

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(request, auth[1])

    def authenticate_credentials(self, request, token):
        public_key = self.get_header_public_key(request)
        key = self.get_key(public_key)
        self.verify(key, self.data_as_string(request.data), token.decode("utf-8"))
        return (self.get_user(key), token)

    def get_header_public_key(self, request):
        return request.META.get("HTTP_PUBLIC_KEY")
