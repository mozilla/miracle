from gzip import GzipFile
from io import BytesIO
import struct
import zlib

from miracle.exceptions import GZIPDecodeError


def gzip_decode(blob, encoding='utf-8'):
    try:
        with GzipFile(None, mode='rb', fileobj=BytesIO(blob)) as gzip_file:
            out = gzip_file.read()
        if encoding:
            return out.decode(encoding)
        return out
    except (IOError, OSError, EOFError, struct.error, zlib.error) as exc:
        raise GZIPDecodeError(repr(exc))


def gzip_encode(blob, encoding='utf-8', compresslevel=6):
    if encoding and isinstance(blob, str):
        blob = blob.encode(encoding)
    out = BytesIO()
    with GzipFile(None, 'wb',
                  compresslevel=compresslevel, fileobj=out) as gzip_file:
        gzip_file.write(blob)
    return out.getvalue()
