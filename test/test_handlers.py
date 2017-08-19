"""
Tests various utility-related
functions in the handlers,
namely those who manipulate
the sidebar and return various
values related to it.
"""

import unittest

from nerodia import handlers


HEADER = "# Streams"


class EmptySidebarTestCase(unittest.TestCase):
    """
    Tests sidebar-manipulation related
    functions with an empty sidebar.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_find_start_idx(self):
        """
        Validates that `find_stream_start_idx`
        returns `None` when the header for the
        streams can not be found in the passed string.
        """

        self.assertIsNone(handlers.find_stream_start_idx(""))


class SidebarWithoutStreamsOnListTestCase(unittest.TestCase):
    """
    A test case which tests various
    sidebar-manipulation related
    functions with a sidebar that
    only contains the `# Streams`
    header and no entries in the
    stream list that should be put
    below the header.
    """

    def setUp(self):
        """
        Assigns a simple sidebar-imitating
        string to the instance attribute
        `sidebar` which should be used in
        the tests of this TestCase. The
        string itself should not be
        manipulated.
        Additionally, assigns the instance
        attribute `start_idx` which indicates
        the position of the last character
        of the Streams header.
        """

        self.sidebar = (
            "Some random testing Sidebar"
            ""
            f"{HEADER}"
            ""
        )
        self.start_idx = self.sidebar.find(HEADER) + len(HEADER) - 1

    def tearDown(self):
        pass

    def test_find_start_idx(self):
        """
        Validates that `find_stream_start_idx`
        properly returns the position of the first
        character after the streams header (`HEADER`),
        so that other functions such as
        `remove_old_stream_list` can use the index
        without any further issues.
        Additionally validates that the first
        character found for the empty sidebar is
        an space, since no streams have been
        added to the streams list.
        """

        start_idx = handlers.find_stream_start_idx(self.sidebar)
        self.assertEqual(handlers.find_stream_start_idx(self.sidebar), self.start_idx)
        self.assertEqual(self.sidebar[start_idx], "s")

    def test_remove_old_list(self):
        """
        Validates that the `remove_old_stream_list`
        function does not change the sidebar since
        there are no streams present in the sidebar
        below the stream header.
        """

        self.assertEqual(
            handlers.remove_old_stream_list(self.sidebar), self.sidebar
        )


class SidebarWithThreeStreamsOnListTestCase(unittest.TestCase):
    """
    A test case with a sidebar that contains
    a list of three streams below the header.
    """

    def setUp(self):
        """
        Adds three instance attributes:
            `sidebar`, which contains a
            sidebar which should be cleaned.

            `clean_sidebar`, which contains a
            "clean" version of the previous
            sidebar, clean meaning that it
            does not contain any entries
            for followed streams anymore.

            `start_idx`, which is the index
            of the last character of the header.
        """

        self.sidebar = (
            "My subreddit sidebar\n"
            f"{HEADER}\n"
            "> some-stream  \n"
            "> another-stream  \n"
            "> test-stream  \n"
            ""
            "my other content\n"
            "> ignore-me-botto"
        )

        self.clean_sidebar = (
            "My subreddit sidebar\n"
            f"{HEADER}\n"
            ""
            "my other content\n"
            "> ignore-me-botto"
        )

        self.start_idx = self.sidebar.find(HEADER) + len(HEADER) - 1

    def tearDown(self):
        pass

    def test_find_start_idx(self):
        """
        Validates that `find_stream_start_idx`
        properly returns the index of the last
        character in the header, as set in the
        `setUp` method under the attribuet `start_idx`.
        """

        self.assertEqual(
            handlers.find_stream_start_idx(self.sidebar), self.start_idx
        )

    def test_remove_old_list(self):
        """
        Validates that `remove_old_stream_list`
        returns the sidebar that was assigned
        to the test case instance in `setUp`,
        but without any entries on the streams
        list as specified in the instance attribute
        `clean_sidebar`.
        """

        self.assertEqual(
            handlers.remove_old_stream_list(self.sidebar), self.clean_sidebar
        )
