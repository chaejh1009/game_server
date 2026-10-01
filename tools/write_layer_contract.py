import json
import os
from datetime import datetime, timezone
from pathlib import Path

# 스파크 집계를 위한 세션
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("layer-contract").getOrCreate()

quarantine_rows = spark.read.parquet(
    "data/lake/quality/parsed-capture-001/quarantine"
).count()

spark.stop()

# 실제 Bronze 지문·행 수와 중복 제거 후 화면 집계를 읽는다.
# 예시: source = json.loads(Path("data/source-manifest.json").read_text())
#       result = json.loads(Path("data/report.json").read_text())
# [문제 1 · 여러 줄] capture-001 manifest와 화면 summary JSON을 각각 bronze와 summary 사전으로 읽는 두 줄을 작성해보세요. (2줄)
bronze = json.loads(Path("data/lake/bronze/game/capture-001/manifest.json").read_text())
summary = json.loads(Path("data/marts/game-summary.json").read_text())

# 입력 버전, Silver·Gold 위치, 중복 제거 키와 집계 기준을 한 계약에 기록한다.
contract = {
    "schema_version": 1, "dataset_version": "capture-001",
    # [문제 2 · 한 단어] 빈칸을 채워보세요.
    "input_sha256": bronze["sha256"],
    "bronze_rows": bronze["rows"],
    # 예시:     "order_rows": report["order_count"],
    # [문제 3 · 한 줄] 중복 제거된 Silver의 행동 수를 summary에서 읽어 silver_rows 항목에 넣는 한 줄을 작성해보세요.
    "silver_rows": summary["event_count"],
    # [문제 4 · 한 단어] 빈칸을 채워보세요.
    "silver_uri": "silver/game_actions/capture-001",
    "gold_uri": "gold/game_daily/capture-001",
    "rules": {
        # [문제 5 · 한 단어] 빈칸을 채워보세요.
        "schema_version": 1, "dedup_key": "event_id",
        # [문제 6 · 한 단어] 빈칸을 채워보세요.
        "calendar_timezone": "Asia/Seoul",
        "gold_grain": ["event_date", "room_id", "event_type"],
    },
    "created_at": datetime.now(timezone.utc).isoformat(),
}

# 다음 교시가 참조할 계층 계약을 저장하고 출력한다.
out = Path("data/contracts/layer-contract.json")
out.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(contract, ensure_ascii=False, indent=2))