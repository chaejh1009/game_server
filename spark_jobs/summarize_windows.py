"""Read finalized Parquet windows and publish at most twenty rows of each kind."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pyspark.sql import SparkSession, functions as F


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument('--rows', type=int, choices=[5, 10, 20], default=20)
    args = parser.parse_args()
    data_dir = Path(args.data_dir).resolve()
    spark = (
        SparkSession.builder.appName("game-window-summary")
        .config("spark.sql.session.timeZone", "Asia/Seoul")
        .getOrCreate()
    )

    rows = []
    try:
        for kind in ["tumbling", "sliding"]:
            source = data_dir / "lake" / "windows" / kind
            if not source.exists() or not any(source.glob("*.parquet")):
                continue
            windows = spark.read.parquet(source.as_uri())
            visible = (
                windows.orderBy(F.desc("window_start"), "event_type")
                .limit(args.rows)
                .select(
                    "kind",
                    F.date_format("window_start", "yyyy-MM-dd'T'HH:mm:ssXXX").alias("window_start"),
                    F.date_format("window_end", "yyyy-MM-dd'T'HH:mm:ssXXX").alias("window_end"),
                    "event_type", "count",
                )
            )
            rows.extend(row.asDict() for row in visible.collect())
        result = {"generated_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(), "windows": rows}
        output = data_dir / "marts" / "windows.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(output)
        print(f"window rows: {len(rows)} -> {output}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()