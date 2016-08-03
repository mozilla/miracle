import hydra

from miracle.config import BLOOM_DOMAIN


def create_bloom_domain(filename=BLOOM_DOMAIN, _bloom=None):
    if _bloom is not None:
        return _bloom

    return hydra.ReadingBloomFilter(filename)
