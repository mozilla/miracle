

def test_domain(bloom_domain):
    assert 'localhost' in bloom_domain
    assert 'somefancydomain.com' not in bloom_domain
