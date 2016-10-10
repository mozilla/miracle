from miracle.scripts import analysis


def test_main(db):
    assert not analysis.main(['dummy', '--script=foo'], _db=db)
    assert analysis.main(['dummy', '--script=example'], _db=db)
