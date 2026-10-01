import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 날짜가 붙은 Silver를 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
silver = spark.read.parquet(args.input)

# 날짜·방·행동 종류별 행동 수와 서로 다른 플레이어 수를 집계해 저장한다.
# 예시: totals = orders.groupBy("store_id").agg(
#           F.count("*").alias("orders"), F.countDistinct("buyer_id").alias("buyers"),
#       )
# [문제 1 · 여러 줄] 날짜·방·행동 종류별 event_count와 서로 다른 player_id 수 active_players를 집계하는 코드를 작성해보세요. (4줄)
daily = silver.groupBy("event_date", "room_id", "event_type").agg(
    F.count("*").alias("event_count"), F.countDistinct("player_id").alias("active_players"),
)
daily.orderBy(
    F.col("event_count").desc(),
    "event_date", "room_id", "event_type").show(30, truncate=False)
# [문제 2 · 한 단어] 빈칸을 채워보세요.
daily.write.mode("errorifexists").partitionBy("event_date").parquet(args.output)

# Gold의 행동 수 합계가 Silver 행 수와 같은지 확인하고 다르면 중단한다.
source_count = silver.count()
# 예시: total_units = items.agg(F.sum("units").alias("n")).first()["n"] or 0
# [문제 3 · 한 줄] Gold의 event_count 합을 첫 행에서 읽고 빈 집계이면 0으로 두는 한 줄을 작성해보세요.
count_sum = daily.agg(F.sum("event_count").alias("n")).first()["n"] or 0
print("source_count =", source_count, "gold_count_sum =", count_sum)
# [문제 4 · 한 단어] 빈칸을 채워보세요.
if source_count != count_sum:
    raise ValueError("aggregation count did not conserve events")
spark.stop()