import sys

class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

TEST_RUNNER = 'webui.tests.utils.UnManagedModelTestRunner'

"""
If we're doing tests, disable migrations so the microbedb
tables get made.
"""
if 'test' in sys.argv or 'test_coverage' in sys.argv:
    MIGRATION_MODULES = DisableMigrations()
