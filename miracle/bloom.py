import hydra

from miracle.config import (
    BLOOM_DOMAIN,
    BLOOM_DOMAIN_SOURCE,
    PUBLIC_SUFFIX_LIST,
)


def create_bloom_domain(bloom_filename=BLOOM_DOMAIN,
                        public_suffix_filename=PUBLIC_SUFFIX_LIST,
                        _bloom=None):
    if _bloom is not None:
        return _bloom

    return BloomDomainFilter(bloom_filename, public_suffix_filename)


def _read_data_file(filename):
    lines = []
    with open(filename, 'rt', encoding='utf-8') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line and not line.startswith('//'):
                line = line.split(' ')[0]
                lines.append(line)
    return lines


def parse_domain_blocklist_source(filename=BLOOM_DOMAIN_SOURCE):
    lines = _read_data_file(filename)
    lines += ['broadcasthost', 'localhost', 'localhost.local']
    return lines


def parse_public_suffix_list(filename=PUBLIC_SUFFIX_LIST):
    lines = _read_data_file(filename)
    lines += ['local']
    return frozenset(lines)


class BloomDomainFilter(object):

    def __init__(self, bloom_filename, public_suffix_filename):
        self.bloom = hydra.ReadingBloomFilter(bloom_filename)
        self.public_suffixes = parse_public_suffix_list(public_suffix_filename)

    def __contains__(self, url):
        return self.tld(url) in self.bloom

    def tld(self, url):
        labels = url.split('.')
        for i in range(0, len(labels)):
            sub_labels = labels[i:]
            full_match = '.'.join(sub_labels)
            exception_match = '!' + full_match
            matches = {
                full_match,
                exception_match,
                '.'.join(['*'] + sub_labels[1:]),
            }
            if exception_match in self.public_suffixes:
                return '.'.join(sub_labels)
            elif matches.intersection(self.public_suffixes):
                return '.'.join(labels[max(i, 1) - 1:])
        return url

    def close(self):
        self.bloom.close()
