"""
Sets the environment variable
NERODIA_DB_PATH up properly to
make sure that the actual database
is not changed through the various
test runs. The environment variable
is reset through calling `finish`.
"""

import os


OLD_DB_PATH = os.environ.get('NERODIA_DB_PATH')


def init():
    """
    Initialize the environment variable.
    The database of Nerodia is put into
    the test directory, named `test.db`.
    """

    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
    TEST_DB_PATH = os.path.join(
        PARENT_DIR, "test", "test.db"
    )
    os.environ['NERODIA_DB_PATH'] = TEST_DB_PATH


def finish():
    """
    Restore the environment variable
    to its original state. If it was
    not set, this function does nothing.
    """

    if OLD_DB_PATH is not None:
        os.environ['NERODIA_DB_PATH'] = OLD_DB_PATH
