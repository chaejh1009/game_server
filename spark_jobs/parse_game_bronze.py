import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 Spark 세션의 시간대를 UTC로 고정한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
# [문제 1 · 한 단어] 빈칸을 채워보세요.
spark.conf.set("spark.sql.session.timeZone", "UTC")

# Kafka 전달 필드와 메시지 본문의 이벤트 필드를 별도 스키마로 정의한다.
outer = "topic STRING, partition INT, offset BIGINT, key STRING, value STRING"
# [문제 2 · 한 단어] 빈칸을 채워보세요.
envelope = T.StructType([
    T.StructField("schema_version", T.IntegerType()),
    T.StructField("event_id", T.StringType()),
    T.StructField("event_type", T.StringType()),
    T.StructField("player_id", T.StringType()),
    T.StructField("room_id", T.StringType()),
    T.StructField("event_time", T.StringType()),
    T.StructField("payload", T.MapType(T.StringType(), T.StringType())),
])

# value를 이벤트로 해석하고 전달 위치와 함께 평평한 표로 펼친다.
raw = spark.read.schema(outer).json(args.input)
# 예시: parsed_orders = source.withColumn("order", F.from_json("body", order_schema))
# [문제 3 · 한 줄] raw의 value를 envelope 스키마로 해석하여 event 열을 추가하는 한 줄을 작성해보세요.
parsed_orders = raw.withColumn("event", F.from_json("value", envelope))

# 예시: flat_orders = parsed_orders.select(
#           "offset", "order.order_id", "order.amount",
#       )
# [문제 4 · 여러 줄] Kafka 전달 위치와 value, event 안의 업무 필드를 선택하여 flat 표로 펼치는 코드를 작성해보세요. (5줄)
flat = parsed_orders.select(
    "topic", "partition", "offset", "value",
    "event.schema_version", "event.event_id", "event.event_type",
    "event.player_id", "event.room_id", "event.event_time", "event.payload",
)

projection = parsed_orders.select(
    "topic","offset", 
    "event.player_id", "event.payload",
)

# 결과를 미리 본 뒤 새 Parquet 경로에 저장한다. 기존 경로가 있으면 중단한다.
projection.show(5, truncate=False)
# [문제 5 · 한 단어] 빈칸을 채워보세요.
flat.write.mode("errorifexists").parquet(args.output)
spark.stop()