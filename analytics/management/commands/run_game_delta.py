import os
import subprocess
import sys
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "기존 Spark 클러스터에서 고유 게임 사실 Delta를 계속 갱신합니다."

    def add_arguments(self, parser):
        parser.add_argument("--topic", default="game.actions.v1")
        parser.add_argument("--data-dir", default=str(settings.DATA_DIR))
        parser.add_argument("--progress-output")

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"]).resolve()
        progress = Path(options["progress_output"]).resolve() if options["progress_output"] else data_dir / "marts" / "progress-game-actions.json"
        command = [
            settings.SPARK_SUBMIT, "--master", settings.SPARK_MASTER,
            "--deploy-mode", "client", "--executor-cores", "1", "--total-executor-cores", "2",
            "--packages", ",".join([settings.KAFKA_PACKAGE, settings.DELTA_PACKAGE]),
            "--conf", f"spark.pyspark.python={sys.executable}",
            "--conf", f"spark.pyspark.driver.python={sys.executable}",
            str(settings.PROJECT_DIR / "game_server" / "spark_jobs" / "game_actions_delta.py"),
            "--data-dir", str(data_dir),
            "--bootstrap-servers", ",".join(settings.KAFKA_BOOTSTRAP_SERVERS),
            "--topic", options["topic"], "--progress-output", str(progress),
        ]
        env = os.environ.copy()
        env["PYSPARK_PYTHON"] = sys.executable
        env["PYSPARK_DRIVER_PYTHON"] = sys.executable
        subprocess.run(command, cwd=settings.BASE_DIR, env=env, check=True)
