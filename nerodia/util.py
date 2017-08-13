"""
Contains utility functions and
variables that can or should be
used in various modules, such as
locks for different variables.
"""

import random
import string
import threading


# Used to verify users. To be used along with the lock defined below.
verify_dict = dict()

# Used for modifications to the verification dictionary.
verify_lock = threading.Lock()


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
