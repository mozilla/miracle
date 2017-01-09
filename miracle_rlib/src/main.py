import os
import os.path
from sys import platform

from cffi import FFI

if platform == 'darwin':
    _ext = 'dylib'
else:
    _ext = 'so'

_libname = 'libmiracle_rlib.%s' % _ext
_variant = 'release'

_here = os.path.dirname(__file__)
_target = os.path.abspath(os.path.join(_here, os.pardir, 'target'))

_ffi = FFI()
_ffi.cdef("""\
    typedef struct {
        char*  serialization;
    } Url;

    Url url_parse(const char *script);
""")

_lib = _ffi.dlopen(os.path.join(_target, _variant, _libname))

# Public API
url_parse = _lib.url_parse

__all__ = ('url_parse', )
