import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 UTC 세션에서 펼친 Bronze 표를 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
p = spark.read.parquet(args.input)

# 시각을 해석하고 조건을 위에서부터 검사해 처음 맞는 사유를 기록한다.
# 예시: timed = events.withColumn("occurred_at", F.try_to_timestamp("time_text"))
# [문제 1 · 한 줄] event_time을 읽을 수 없는 경우 null이 되도록 해석하여 parsed_time 열을 추가하는 한 줄을 작성해보세요.
checked = p.withColumn("parsed_time", F.try_to_timestamp("event_time"))
checked = checked.withColumn("reason",
    F.when(F.col("schema_version") != 1, "unsupported_schema")
     .when(F.col("schema_version").isNull(), "missing_schema")
     # [문제 2 · 한 단어] 빈칸을 채워보세요.
     .when(F.col("event_id").isNull(), "missing_event_id")
     .when(F.col("room_id").isNull(), "missing_room")
     .when(F.col("parsed_time").isNull(), "invalid_time")
     .when(~F.col("event_type").isin(
         "player.moved", "player.gathered", "player.trained"
     ), "unknown_action")
     .when(F.col("event_type").isNull(), "missing_action")
     # [문제 3 · 한 단어] 빈칸을 채워보세요.
     .otherwise("accepted")
)

# 사유별 건수를 확인하고 정상·격리 결과를 각각 새 경로에 저장한다.
# [문제 4 · 한 단어] 빈칸을 채워보세요.
checked.groupBy("reason").count().orderBy("reason").show()
# 예시: clean.filter(F.col("status") == "ready").write.mode("errorifexists").parquet(
#           args.output + "/ready"
#       )

# accepted행을 따로 만들고, projection에서 reason 유지.
accepted = checked.filter(F.col("reason") == "accepted").select(
    "event_id", "room_id", "event_type", "parsed_time", "reason"
)

accepted.groupBy("room_id").count().orderBy("room_id").show()

# [문제 5 · 여러 줄] reason이 accepted인 행만 골라 새 accepted 하위 Parquet 경로에 저장하는 코드를 작성해보세요. (3줄)
checked.filter(F.col("reason") == "accepted").write.mode("errorifexists").parquet(
    args.output + "/accepted"
)

# [문제 6 · 한 단어] 빈칸을 채워보세요.
checked.filter(F.col("reason") != "accepted").write.mode("errorifexists").parquet(
    args.output + "/quarantine"
)
spark.stop()