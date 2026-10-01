import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# UTC 세션에서 중복 제거된 입력을 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
# 예시: session.conf.set("spark.sql.session.timeZone", "Asia/Tokyo")
# [문제 1 · 한 줄] Spark 세션의 시각 해석 기준을 UTC로 설정하는 한 줄을 작성해보세요.
spark.conf.set("spark.sql.session.timeZone", "UTC")
p = spark.read.parquet(args.input)

# 한국 달력 날짜를 계산하고 날짜별 새 Parquet 경로에 저장한다.
# 예시: dated_orders = orders.withColumn(
#           "local_day", F.to_date(F.from_utc_timestamp("created_at", "Asia/Tokyo"))
#       )
# [문제 2 · 여러 줄] parsed_time의 UTC 시각을 서울 시각으로 바꾼 뒤 달력 날짜 event_date를 추가하는 코드를 작성해보세요. (3줄)
dated = p.withColumn(
    "event_date", F.to_date(F.from_utc_timestamp("parsed_time", "Asia/Seoul"))
)
dated.select("event_time", "parsed_time", "event_date").show(10, truncate=False)

# [문제 3 · 한 단어] 빈칸을 채워보세요.
dated.write.mode("errorifexists").partitionBy("event_date").parquet(args.output)

# 한국 자정 직전·직후의 UTC 시각으로 날짜 경계를 확인한다.
boundary = spark.createDataFrame([
    ("2026-09-11T14:59:59Z",),
    ("2026-09-11T15:00:00Z",),

    ("2026-09-11T00:00:00Z",),
], ["text_time"])
boundary.select(
    "text_time",
    # [문제 4 · 한 단어] 빈칸을 채워보세요.
    F.to_date(F.from_utc_timestamp(F.to_timestamp("text_time"), "Asia/Seoul")).alias("date")
).show(truncate=False)
spark.stop()