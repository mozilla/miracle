from base64 import (
    b64decode,
)

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from miracle import config
from miracle.log import LOGGER


def create_crypto(private_key=config.PRIVATE_KEY,
                  public_key=config.PUBLIC_KEY, _crypto=None):
    if _crypto is not None:
        return _crypto
    return Crypto(private_key=private_key, public_key=public_key)


class Crypto(object):

    _backend = None
    _private = None
    _public = None

    def __init__(self, private_key=None, public_key=None):
        self._backend = default_backend()
        if private_key:
            self._private = self._load_private(private_key)
        if public_key:
            self._public = self._load_public(public_key)

    def _load_private(self, data):
        try:
            return serialization.load_pem_private_key(
                b64decode(data), password=None, backend=self._backend)
        except Exception:  # pragma: no cover
            LOGGER.error(
                'Failed to parse private key starting with: %s', data[:28])

    def _load_public(self, data):
        try:
            return serialization.load_pem_public_key(
                b64decode(data), backend=self._backend)
        except Exception:  # pragma: no cover
            LOGGER.error(
                'Failed to parse public key starting with: %s', data[:26])

    def encrypt(self, plaintext):
        try:
            ciphertext = self._public.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                )
            )
        except Exception:
            raise ValueError("Couldn't encrypt message.")
        return ciphertext

    def decrypt(self, ciphertext):
        try:
            plaintext = self._private.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except Exception:
            raise ValueError("Couldn't decrypt message.")
        return plaintext
