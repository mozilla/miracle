from miracle.scripts import analysis


def test_main(db):
    assert analysis.main(['dummy', '--script=foo'], _db=db) == 1
    assert analysis.main(['dummy', '--script=example'], _db=db) is None
