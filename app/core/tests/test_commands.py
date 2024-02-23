"""Test custom django management commands"""

# we're gonna mock the database, so that's why line below
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# in the decorator, first we have directory of the tested file. "check" is used to simulate a response
@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db if the db is ready"""

        patched_check.return_value = True
        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    # patched_sleep is from the decorator right above, patched_check from the one above class
    # order of args is important. Django picks args inside-out 
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """test waiting for db when getting OperationalError"""
        # first 2 times we raise psycopg2 error, then 3 times OperationalError, then True
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
