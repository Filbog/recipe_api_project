"""Django command to wait for the db to be available"""
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

import time
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Django commmand to wait for database."""

    def handle(self, *args, **options):
        # this will be shown in console
        self.stdout.write("Waiting for database...")
        # boolean value to track if our db is up yet
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("db unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Databasa available!"))
