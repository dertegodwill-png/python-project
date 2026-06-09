from django.core.management.base import BaseCommand, CommandError
from django.core import management
import os


class Command(BaseCommand):
    help = (
        "Export (dumpdata) or import (loaddata) project data to ease migration from SQLite to Postgres.\n"
        "Usage:\n"
        "  # export locally:\n"
        "  python manage.py migrate_to_postgres --export-file data.json\n"
        "  # upload data.json to the remote service and, after DATABASE_URL points to Postgres and migrations applied:\n"
        "  python manage.py migrate_to_postgres --load --export-file data.json\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--export-file",
            "-e",
            dest="export_file",
            default="data.json",
            help="Path to write/read the fixture file",
        )
        parser.add_argument(
            "--load",
            "-l",
            action="store_true",
            dest="load",
            help="If set, load (loaddata) the specified fixture into the current DB",
        )

    def handle(self, *args, **options):
        fpath = options["export_file"]
        if options["load"]:
            if not os.path.exists(fpath):
                raise CommandError(f"Fixture file not found: {fpath}")
            self.stdout.write(f"Loading data from {fpath} into current database...")
            try:
                management.call_command("loaddata", fpath)
            except Exception as exc:
                raise CommandError(f"Failed to load data: {exc}")
            self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
            return

        # Export path
        self.stdout.write(f"Exporting project data to {fpath}...")
        try:
            # Use dumpdata with natural keys to improve portability
            with open(fpath, "w", encoding="utf-8") as out:
                management.call_command(
                    "dumpdata",
                    "--natural-primary",
                    "--natural-foreign",
                    "--indent",
                    "2",
                    stdout=out,
                )
        except Exception as exc:
            raise CommandError(f"Failed to export data: {exc}")

        size = os.path.getsize(fpath)
        self.stdout.write(self.style.SUCCESS(f"Wrote {fpath} ({size} bytes)"))
