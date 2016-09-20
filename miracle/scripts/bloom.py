import argparse
import os
import shutil
import sys

import hydra

from miracle.bloom import parse_domain_blocklist_source
from miracle.config import BLOOM_DOMAIN_SOURCE
from miracle.log import configure_logging


def create(in_filename, out_filename, archive_path, tmp_path):
    out_filepath = os.path.join(tmp_path, out_filename)

    lines = parse_domain_blocklist_source(in_filename)

    with hydra.WritingBloomFilter(len(lines), 0.0001, out_filepath) as bf:
        for line in lines:
            bf[(line.encode('utf-8'))] = 0

    # Create a tar archive in /tmp/block.dat.tar
    shutil.make_archive(archive_path, 'tar', tmp_path)


def main(in_filename, base='/tmp'):
    # Convert from data/block.txt to block.dat
    out_filename = '.'.join(
        os.path.splitext(os.path.basename(in_filename))[:-1] + ('dat', ))

    archive_path = os.path.join(base, 'output')
    try:
        tmp_path = os.path.join(base, 'archive')
        os.makedirs(tmp_path)
        create(in_filename, out_filename, archive_path, tmp_path)
    finally:
        shutil.rmtree(tmp_path)


def console_entry():  # pragma: no cover
    configure_logging()
    argv = sys.argv

    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='Create bloom filter from blocklist file.')
    parser.add_argument('filename',
                        help='Path to the blocklist file, e.g. %s' %
                             BLOOM_DOMAIN_SOURCE)

    args = parser.parse_args(argv[1:])
    filename = os.path.abspath(args.filename)
    if not os.path.isfile(filename):
        print('File not found.')
        sys.exit(1)

    main(filename)
