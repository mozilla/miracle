from miracle import bloom


def test_domain(bloom_domain):
    assert 'localhost' in bloom_domain
    assert 'somefancydomain.com' not in bloom_domain


def test_read_source():
    lines = bloom.read_source()
    assert 'localhost' in lines
    assert '' not in lines
    assert not [line for line in lines if '//' in line]
