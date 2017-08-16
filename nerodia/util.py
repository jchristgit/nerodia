"""
Contains utility functions and
variables that can or should be
used in various modules, such as
locks for different variables.
"""

import random
import string
import threading


# Used for any statement execution calls to the database.
db_lock = threading.Lock()

# Used for any invocation of PRAW functions.
reddit_lock = threading.Lock()

# A Discord ID -> verification token mapping.
token_dict = dict()

# Used for modifications and access to above dictionary.
token_lock = threading.Lock()

# Used for any queries to the Twitch API.
twitch_lock = threading.Lock()

# Used to verify users. To be used along with the lock defined below.
verify_dict = dict()

# Used for modifications to the verification dictionary.
verify_lock = threading.Lock()


def random_string(length: int = 15):
    """
    Returns a string made up from
    random characters.

    Arguments:
        length (int):
            The length of the string to generate.
            Defaults to 15.

    Returns:
        str: A random string, as long as specified
             with the `length` argument (default: 15).
    """

    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def remove_token(user_id: str):
    """
    Removes the given user ID from the token dict,
    along with the token which the user may or may not
    have used for connecting his Discord account with
    his reddit account for easy execution of commands.

    Arguments:
        user_id (str): The user ID which should be removed from the dict.
    """

    with token_lock:
        del token_dict[user_id]
