import os
import shutil
import tempfile

import hydra
import pytest

from miracle.scripts import bloom


@pytest.yield_fixture(scope='function')
def tmp_path():
    try:
        path = tempfile.mkdtemp()
        yield path
    finally:
        shutil.rmtree(path)


def test_bloom_create(tmp_path):
    in_filename = os.path.join(tmp_path, 'bloom.txt')
    with open(in_filename, 'wt') as fd:
        fd.write('example.com\n')
        fd.write('www.example.com\n')

    archive_path = os.path.join(tmp_path, 'output')
    bloom.create(in_filename, 'bloom.dat', archive_path, tmp_path)

    # Files were created.
    assert os.path.isfile(archive_path + '.tar')
    bloom_path = os.path.join(tmp_path, 'bloom.dat')
    assert os.path.isfile(bloom_path)
    assert os.path.isfile(bloom_path + '.desc')

    with hydra.ReadingBloomFilter(bloom_path) as bf:
        assert 'example.com' in bf
        assert 'www.example.com' in bf
        assert 'foo.com' not in bf


def test_bloom_main(tmp_path):
    in_filename = os.path.join(tmp_path, 'bloom.txt')
    with open(in_filename, 'wt') as fd:
        fd.write('example.com\n')
        fd.write('www.example.com\n')

    bloom.main(in_filename, base=tmp_path)
    assert sorted(os.listdir(tmp_path)) == ['bloom.txt', 'output.tar']
