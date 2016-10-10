"""
Tests for the example analysis script.
"""

from miracle.analysis import example


def test_main(db):
    assert example.main(db) is None


def test_example(db):
    assert example.example(db)
