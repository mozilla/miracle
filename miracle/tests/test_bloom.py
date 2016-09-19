from miracle import bloom


def test_domain(bloom_domain):
    assert 'broadcasthost' in bloom_domain
    assert 'localhost' in bloom_domain
    assert 'localhost.local' in bloom_domain
    assert 'b.localhost.local' in bloom_domain
    assert 'example.local' in bloom_domain
    assert 'a.b.example.local' in bloom_domain
    assert 'reader' in bloom_domain
    assert 'sex.com' in bloom_domain
    assert 'www.sex.com' in bloom_domain
    assert 'a.b.sex.com' in bloom_domain
    assert 'example.adult' in bloom_domain
    assert 'a.b.example.adult' in bloom_domain
    assert 'example.xxx' in bloom_domain
    assert 'a.b.example.xxx' in bloom_domain
    assert 'stevipark18.blogspot.co.id' in bloom_domain
    assert 'not-blocked.com' not in bloom_domain
    assert 'www.not-blocked.com' not in bloom_domain


def test_parse_domain_blocklist_source():
    lines = bloom.parse_domain_blocklist_source()
    assert 'sex.com' in lines
    assert '' not in lines
    assert not [line for line in lines if '//' in line]


def test_parse_public_suffix_list():
    lines = bloom.parse_public_suffix_list()
    assert 'local' in lines
    assert '' not in lines
    assert not [line for line in lines if '//' in line]


def test_tld(bloom_domain):
    # Test cases based on:
    # https://github.com/publicsuffix/list/blob/master/tests/test_psl.txt
    # Invalid hostnames.
    assert bloom_domain.tld('broadcasthost') is None
    assert bloom_domain.tld('reader') is None
    # Listed, but non-Internet, TLD.
    assert bloom_domain.tld('localhost') is None
    assert bloom_domain.tld('localhost.local') == 'localhost.local'
    assert bloom_domain.tld('b.localhost.local') == 'localhost.local'
    assert bloom_domain.tld('a.b.localhost.local') == 'localhost.local'
    # TLD with only 1 rule.
    assert bloom_domain.tld('domain.biz') == 'domain.biz'
    assert bloom_domain.tld('b.domain.biz') == 'domain.biz'
    assert bloom_domain.tld('a.b.domain.biz') == 'domain.biz'
    # TLD with some 2-level rules.
    assert bloom_domain.tld('example.com') == 'example.com'
    assert bloom_domain.tld('b.example.com') == 'example.com'
    assert bloom_domain.tld('a.b.example.com') == 'example.com'
    assert bloom_domain.tld('example.co.uk') == 'example.co.uk'
    assert bloom_domain.tld('www.example.co.uk') == 'example.co.uk'
    assert bloom_domain.tld('uk.com') == 'uk.com'
    assert bloom_domain.tld('example.uk.com') == 'example.uk.com'
    assert bloom_domain.tld('b.example.uk.com') == 'example.uk.com'
    assert bloom_domain.tld('a.b.example.uk.com') == 'example.uk.com'
    assert bloom_domain.tld('test.ac') == 'test.ac'
    # TLD with only 1 (wildcard) rule.
    assert bloom_domain.tld('c.mm') == 'c.mm'
    assert bloom_domain.tld('b.c.mm') == 'b.c.mm'
    assert bloom_domain.tld('a.b.c.mm') == 'b.c.mm'
    # More complex TLD.
    assert bloom_domain.tld('test.jp') == 'test.jp'
    assert bloom_domain.tld('www.test.jp') == 'test.jp'
    assert bloom_domain.tld('ac.jp') == 'ac.jp'
    assert bloom_domain.tld('test.ac.jp') == 'test.ac.jp'
    assert bloom_domain.tld('www.test.ac.jp') == 'test.ac.jp'
    assert bloom_domain.tld('kyoto.jp') == 'kyoto.jp'
    assert bloom_domain.tld('test.kyoto.jp') == 'test.kyoto.jp'
    assert bloom_domain.tld('ide.kyoto.jp') == 'ide.kyoto.jp'
    assert bloom_domain.tld('b.ide.kyoto.jp') == 'b.ide.kyoto.jp'
    assert bloom_domain.tld('a.b.ide.kyoto.jp') == 'b.ide.kyoto.jp'
    assert bloom_domain.tld('c.kobe.jp') == 'c.kobe.jp'
    assert bloom_domain.tld('b.c.kobe.jp') == 'b.c.kobe.jp'
    assert bloom_domain.tld('a.b.c.kobe.jp') == 'b.c.kobe.jp'
    assert bloom_domain.tld('city.kobe.jp') == 'city.kobe.jp'
    assert bloom_domain.tld('www.city.kobe.jp') == 'city.kobe.jp'
    # TLD with a wildcard rule and exceptions.
    assert bloom_domain.tld('test.ck') == 'test.ck'
    assert bloom_domain.tld('b.test.ck') == 'b.test.ck'
    assert bloom_domain.tld('a.b.test.ck') == 'b.test.ck'
    assert bloom_domain.tld('www.ck') == 'www.ck'
    assert bloom_domain.tld('www.www.ck') == 'www.ck'
