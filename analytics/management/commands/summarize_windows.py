import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Publish finalized request-window rows to windows.json."

    def add_arguments(self, parser):
        parser.add_argument("--data-dir", default=str(settings.DATA_DIR))
        parser.add_argument('--rows', type=int, choices=[5, 10, 20], default=20)

    def handle(self, *args, **options):
        command = [
            str(settings.SPARK_SUBMIT), "--master", settings.SPARK_MASTER, "--deploy-mode", "client",
            "--executor-cores", "1", "--total-executor-cores", "2",
            "--conf", f"spark.pyspark.python={sys.executable}",
            "--conf", f"spark.pyspark.driver.python={sys.executable}",
            str(settings.PROJECT_DIR / "game_server" / "spark_jobs" / "summarize_windows.py"),
            '--data-dir', str(Path(options['data_dir']).resolve()),
            '--rows', str(options['rows']),
        ]
        env = os.environ.copy()
        env["PYSPARK_PYTHON"] = sys.executable
        env["PYSPARK_DRIVER_PYTHON"] = sys.executable
        try:
            subprocess.run(command, cwd=settings.BASE_DIR, env=env, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise CommandError("Window summary did not complete; preserve the previous JSON.") from exc