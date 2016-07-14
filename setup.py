import os

from setuptools import (
    find_packages,
    setup,
)

from miracle import VERSION

here = os.path.relpath(os.path.abspath(os.path.dirname(__file__)))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as fd:
    long_description = fd.read()

setup(
    name='mozilla-miracle',
    version=VERSION,
    description='Mozilla Miracle',
    long_description=long_description,
    url='https://github.com/mozilla/miracle',
    author='Mozilla',
    author_email='context-graph@lists.mozilla.org',
    license='MPL 2.0',
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: Pyramid',
    ],
    keywords='mozilla miracle',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
