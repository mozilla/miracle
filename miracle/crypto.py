from base64 import b64decode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jwcrypto.jwe import JWE
from jwcrypto.jwk import JWK

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
    _private_jwk = None
    _public = None
    _public_jwk = None

    def __init__(self, private_key=None, public_key=None):
        self._backend = default_backend()
        if private_key:
            self._load_private(private_key)
        if public_key:
            self._load_public(public_key)

    def _load_private(self, data):
        try:
            self._private = serialization.load_pem_private_key(
                b64decode(data), password=None, backend=self._backend)
            self._private_jwk = JWK()
            self._private_jwk.import_from_pyca(self._private)
        except Exception:  # pragma: no cover
            LOGGER.error(
                'Failed to parse private key starting with: %s', data[:28])

    def _load_public(self, data):
        try:
            self._public = serialization.load_pem_public_key(
                b64decode(data), backend=self._backend)
            self._public_jwk = JWK()
            self._public_jwk.import_from_pyca(self._public)
        except Exception:  # pragma: no cover
            LOGGER.error(
                'Failed to parse public key starting with: %s', data[:26])

    def encrypt(self, plaintext,
                _protected='{"alg":"RSA-OAEP","enc":"A256GCM"}',
                _public_jwk=None):
        try:
            jwe = JWE(plaintext=plaintext,
                      protected=_protected)
            _public_jwk = _public_jwk if _public_jwk else self._public_jwk
            jwe.add_recipient(_public_jwk)
            ciphertext = jwe.serialize(compact=True)
        except Exception:
            raise ValueError("Couldn't encrypt message.")
        return ciphertext

    def decrypt(self, ciphertext):
        try:
            jwe = JWE()
            jwe.deserialize(ciphertext, key=self._private_jwk)
            plaintext = jwe.payload.decode('utf-8')
        except Exception:
            raise ValueError("Couldn't decrypt message.")
        return plaintext

    def validate(self, ciphertext):
        try:
            jwe = JWE()
            jwe.deserialize(ciphertext)
            if jwe.jose_header != {'alg': 'RSA-OAEP', 'enc': 'A256GCM'}:
                return False
        except Exception:
            return False
        return True
