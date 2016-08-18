import pytest


def test_encrypt(crypto):
    data = crypto.encrypt(b'{"foo": 1, "bar": []}')
    assert isinstance(data, bytes)
    assert b'{"foo' not in data


def test_encrypt_fail(crypto):
    with pytest.raises(ValueError):
        crypto.encrypt('')


def test_decrypt(crypto):
    data = crypto.encrypt(b'{"foo": 1, "bar": []}')
    assert crypto.decrypt(data) == b'{"foo": 1, "bar": []}'


def test_decrypt_fail(crypto):
    with pytest.raises(ValueError):
        crypto.decrypt(b'plain text')
