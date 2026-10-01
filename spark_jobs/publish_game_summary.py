import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# Silver 입력과 화면용 JSON 출력 경로를 받는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
import json
from datetime import datetime, timezone
from pathlib import Path

# 행동별·방별 집계를 정렬하고 방 수가 100개를 넘으면 수집을 중단한다.
silver = spark.read.parquet(args.input)
actions = silver.groupBy("event_type").count().orderBy("event_type")
rooms = silver.groupBy("room_id").count().orderBy("room_id")
# 예시: if stores.count() > 50:
#           raise ValueError("too many stores")
# [문제 1 · 여러 줄] 방별 집계가 100개를 초과하면 ValueError로 수집을 중단하는 조건문을 작성해보세요. (2줄)
if rooms.count() > 100:
    raise ValueError("too many stores")

# 작은 집계만 드라이버로 가져와 생성 시각과 함께 화면용 사전에 담는다.
summary = {
    "dataset_version":"capture-001",
    "schema_version": 1,
    # [문제 2 · 한 단어] 빈칸을 채워보세요.
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "event_count": silver.count(),
    # [문제 3 · 한 단어] 빈칸을 채워보세요.
    "by_action": [r.asDict() for r in actions.collect()],
    "by_room": [r.asDict() for r in rooms.collect()],
}

# 완성한 JSON을 임시 파일에 쓴 뒤 최종 화면 파일로 교체한다.
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
tmp = out.with_suffix(out.suffix + ".tmp")
# 예시: draft.write_text(json.dumps(report, ensure_ascii=False, indent=4), encoding="utf-8")
# [문제 4 · 한 줄] summary를 한글이 보존되는 들여쓰기 2칸 JSON으로 바꾸어 UTF-8 임시 파일에 쓰는 한 줄을 작성해보세요.
tmp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
# [문제 5 · 한 단어] 빈칸을 채워보세요.
tmp.replace(out)
print(json.dumps(summary, ensure_ascii=False, indent=2))
spark.stop()