import pytest


def test_jwk(crypto):
    priv = crypto._private_jwk
    assert priv.key_type == 'RSA'
    pub = crypto._public_jwk
    assert pub.key_type == 'RSA'
    assert priv.thumbprint() == pub.thumbprint()


def test_pyca(crypto):
    assert crypto._private.key_size == 2048
    assert crypto._public.key_size == 2048


def test_encrypt(crypto):
    data = crypto.encrypt(b'{"foo": 1, "bar": []}')
    assert isinstance(data, str)
    assert '{"foo' not in data


def test_encrypt_fail(crypto):
    with pytest.raises(ValueError):
        crypto.encrypt(None)


def test_decrypt(crypto):
    data = crypto.encrypt(b'{"foo": 1, "bar": []}')
    assert crypto.decrypt(data) == b'{"foo": 1, "bar": []}'


def test_decrypt_fail(crypto):
    with pytest.raises(ValueError):
        crypto.decrypt(None)
