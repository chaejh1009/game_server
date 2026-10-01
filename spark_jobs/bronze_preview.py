import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입력 경로를 받고 Spark에서 사용할 Kafka 원본 스키마를 정한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-bronze-preview").getOrCreate()
# 예시: sample_schema = T.StructType([
#           T.StructField("name", T.StringType()),
#       ])
# [문제 1 · 여러 줄] topic·key·value는 StringType, partition은 IntegerType, offset은 LongType인 Kafka 원본 schema를 작성해보세요. (7줄)
sample_schema = T.StructType([
    T.StructField("topic", T.StringType()),
    T.StructField("key", T.StringType()),
    T.StructField("value", T.StringType()),
    T.StructField("partition", T.IntegerType()),
    T.StructField("offset", T.LongType()),
])

# 원본 전달 위치를 미리 보고 파티션별 행 수와 offset 범위를 확인한다.
# 예시: events = spark.read.schema(event_schema).json(source_path)
# [문제 2 · 한 줄] 정한 schema를 적용해 입력 JSON을 raw로 읽어오는 한 줄을 작성해보세요.
raw = spark.read.schema(sample_schema).json(args.input)
raw.select("topic", "partition", "offset").show(5, truncate=False)
# [문제 3 · 한 단어] 빈칸을 채워보세요.
raw.groupBy("partition").agg(
    F.count("*").alias("rows"),
    F.min("offset").alias("first_offset"),
    # [문제 4 · 한 단어] 빈칸을 채워보세요.
    F.max("offset").alias("last_offset"),
    F.countDistinct('key'),
).orderBy("partition").show(truncate=False)

# 실제 실행 Master를 확인한 뒤 Spark 세션을 닫는다.
print("master =", spark.sparkContext.master)
spark.stop()