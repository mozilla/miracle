import pytest

from miracle.exceptions import GZIPDecodeError
from miracle import util


def test_gzip_decode():
    assert util.gzip_decode(util.gzip_encode('foo')) == 'foo'
    assert util.gzip_decode(util.gzip_encode('foo'), encoding=None) == b'foo'
    with pytest.raises(GZIPDecodeError):
        util.gzip_decode(b'invalid')


def test_gzip_encode():
    assert isinstance(util.gzip_encode('foo'), bytes)
    assert isinstance(util.gzip_encode(b'foo', encoding=None), bytes)
