"""
Contains utility functions that
can be used in various modules.
"""

import string
import random


def random_string(length: int = 5):
    """
    Returns a string made up from
    random characters.

    Arguments:
        length (int)
            The length of the string to generate.
            Defaults to 5.

    Returns:
        str: A random string, as long as specified
             with the `length` argument (default: 5).
    """

    return ''.join(random.choice(string.ascii_letters) for _ in range(length))
