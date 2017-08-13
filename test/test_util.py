"""
Tests the various utility functions
that are used in nerodia.
"""

import string

from nerodia import util


def test_random_string():
    """
    Validates that the `random_string`
    function properly returns strings
    of the given length, defaulting to 5.
    """

    rand_str = util.random_string()

    assert isinstance(rand_str, str)
    assert len(rand_str) == 5
    assert all(c in string.printable for c in rand_str)

    assert len(util.random_string(0)) == 0
    assert len(util.random_string(10)) == 10
    assert len(util.random_string(15)) == 15
