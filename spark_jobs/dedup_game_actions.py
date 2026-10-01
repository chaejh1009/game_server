import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 검사에 통과한 표를 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
from pyspark.sql.window import Window
p = spark.read.parquet(args.input)

# 업무 필드의 지문을 만들며 payload 항목 순서를 정렬해 표현 차이를 없앤다.
business = ["schema_version", "event_id", "event_type", "player_id",
            "room_id", "event_time", "payload"]
fingerprints = p.withColumn("body_hash", F.sha2(F.to_json(F.struct(
    *[F.col(name) for name in business if name != "payload"],
    # [문제 1 · 한 단어] 빈칸을 채워보세요.
    F.sort_array(F.map_entries("payload")).alias("payload")
)), 256))

# 같은 event_id의 업무 내용이 다르면 임의 선택하지 않고 중단한다.
conflicts = fingerprints.groupBy("event_id").agg(
    # [문제 2 · 한 단어] 빈칸을 채워보세요.
    F.countDistinct("body_hash").alias("variants")
).filter(F.col("variants") > 1)
if conflicts.limit(1).count():
    conflicts.show(truncate=False)
    raise ValueError("same event_id has different business content")

# 동일 행동에서는 topic·partition·offset 순서로 대표 전달 한 건을 고른다.
# 예시: rank_window = Window.partitionBy("order_id").orderBy("received_at", "sequence")
# [문제 3 · 한 줄] 같은 event_id를 한 윈도로 묶고 topic·partition·offset 순서로 정렬하는 한 줄을 작성해보세요.
rank_window = Window.partitionBy("event_id").orderBy("topic", "partition", "offset")

# 예시: latest = records.withColumn("rank", F.row_number().over(rank_window)).filter(
#           F.col("rank") == 1
#       ).drop("rank", "raw_text")
# [문제 4 · 여러 줄] 윈도별 순번 1번만 남기고 임시 열 rn·body_hash 및 검사·원문 열 reason·value를 제거하는 코드를 작성해보세요. (3줄)
silver = fingerprints.withColumn("rn", F.row_number().over(rank_window)).filter(
    F.col("rn") == 1
).drop("rn", "body_hash", "reason", "value")

accepted = p.count()
logical = silver.count()

duplicate_deliveries = accepted - logical

print("=" * 50)
print("=" * 50)
print("=" * 50)
print("accepted : ", accepted)
print("logical : ", logical)
print("duplicate_deliveries : ", duplicate_deliveries)
print("=" * 50)
print("=" * 50)
print("=" * 50)

# 전달 수와 논리 행동 수를 확인하고 기존 결과를 덮어쓰지 않고 저장한다.
print("accepted =", p.count(), "logical =", silver.count())
silver.write.mode("errorifexists").parquet(args.output)
spark.stop()