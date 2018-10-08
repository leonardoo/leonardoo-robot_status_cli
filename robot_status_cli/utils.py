from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from robot_status_cli.compat import get_bytes_from_str


def get_token_generator(secret_key):
    backend = default_backend()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=secret_key.encode(),
        iterations=100000,
        backend=backend
    )
    return kdf

def verify_token(secret_key, data, token):
    kdf = get_token_generator(secret_key)
    kdf.verify(data.encode(), get_bytes_from_str(token))
