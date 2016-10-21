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
    data = crypto.encrypt('{"foo": 1, "bar": []}')
    assert isinstance(data, str)
    assert '{"foo' not in data

    with pytest.raises(ValueError):
        crypto.encrypt(None)


def test_decrypt(crypto):
    data = crypto.encrypt('{"foo": 1, "bar": []}')
    assert crypto.decrypt(data) == '{"foo": 1, "bar": []}'

    with pytest.raises(ValueError):
        crypto.decrypt(None)


def test_validate(crypto):
    data = crypto.encrypt('{"foo": 1, "bar": []}')
    assert crypto.validate(data)
    assert not crypto.validate(b'garbage')
    assert not crypto.validate('garbage')

    data = crypto.encrypt(
        '{"foo": 1}', _protected='{"alg":"RSA-OAEP","enc":"A128CBC-HS256"}')
    assert not crypto.validate(data)
    data = crypto.encrypt(
        '{"foo": 1}', _protected='{"alg":"RSA1_5","enc":"A256GCM"}')
    assert not crypto.validate(data)
