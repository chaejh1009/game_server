import os
import subprocess
import sys
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "기존 Spark 클러스터에서 게임 전달 레코드의 시간 창을 계산합니다."
    def add_arguments(self, parser):
        parser.add_argument("--kind", choices=["tumbling", "sliding"], default="tumbling")
        parser.add_argument("--topic", default="game.actions.v1")
        parser.add_argument("--data-dir", default=str(settings.DATA_DIR))

    def handle(self, *args, **options):
        command = [
            settings.SPARK_SUBMIT, "--master", settings.SPARK_MASTER,
            "--deploy-mode", "client", "--executor-cores", "1", "--total-executor-cores", "2",
            "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.3",
            "--conf", f"spark.pyspark.python={sys.executable}",
            "--conf", f"spark.pyspark.driver.python={sys.executable}",
            str(settings.PROJECT_DIR / "game_server" / "spark_jobs" / "game_windows.py"),
            "--data-dir", str(Path(options["data_dir"]).resolve()),
            "--bootstrap-servers", ",".join(settings.KAFKA_BOOTSTRAP_SERVERS),
            "--topic", options["topic"], "--kind", options["kind"],
        ]
        env = os.environ.copy()
        env["PYSPARK_PYTHON"] = sys.executable
        env["PYSPARK_DRIVER_PYTHON"] = sys.executable
        subprocess.run(command, cwd=settings.BASE_DIR, env=env, check=True)