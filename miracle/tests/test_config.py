import base64

from miracle import config


def test_keys():
    assert isinstance(config.PRIVATE_KEY, bytes)
    assert base64.b64decode(
        config.PRIVATE_KEY).startswith(b'-----BEGIN PRIVATE KEY-----\n')
    assert isinstance(config.PUBLIC_KEY, bytes)
    assert base64.b64decode(
        config.PUBLIC_KEY).startswith(b'-----BEGIN PUBLIC KEY-----\n')
