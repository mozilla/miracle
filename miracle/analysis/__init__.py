import importlib
import pkgutil

HERE = __path__  # NOQA


def locate_modules():
    # Locate all modules in this sub-package.
    names = [name for _, name, ispkg in
             pkgutil.iter_modules(HERE) if not ispkg]

    result = {}
    for name in names:
        module = importlib.import_module('miracle.analysis.' + name)
        result[name] = module

    return result

MODULES = locate_modules()
