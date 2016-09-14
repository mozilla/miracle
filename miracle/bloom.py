import hydra

from miracle.config import (
    BLOOM_DOMAIN,
    BLOOM_DOMAIN_SOURCE,
    PUBLIC_SUFFIX_LIST,
)


def read_source(filename=BLOOM_DOMAIN_SOURCE):
    lines = []
    with open(filename, 'rt', encoding='utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line and not line.startswith('//'):
                lines.append(line)
    return lines


def create_bloom_domain(bloom_filename=BLOOM_DOMAIN,
                        public_suffix_filename=PUBLIC_SUFFIX_LIST,
                        _bloom=None):
    if _bloom is not None:
        return _bloom

    return BloomDomainFilter(bloom_filename, public_suffix_filename)


class BloomDomainFilter(object):

    def __init__(self, bloom_filename, public_suffix_filename):
        self.bloom = hydra.ReadingBloomFilter(bloom_filename)
        self.public_suffix = public_suffix_filename

    def __contains__(self, url):
        return url in self.bloom

    def close(self):
        self.bloom.close()
