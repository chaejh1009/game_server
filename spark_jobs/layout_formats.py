import argparse
from pyspark.sql import SparkSession, functions as F

# 동일한 입력을 읽어 JSON과 Parquet 비교를 준비한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)

# payload를 제외한 같은 열을 무압축 JSON과 Snappy Parquet으로 각각 새로 저장한다.
# 예시: comparison = source.drop("details")
# [문제 1 · 한 줄] JSON과 Parquet 비교에서 payload 열을 제외한 plain 표를 만드는 한 줄을 작성해보세요.
plain = df.drop("payload")
# 전체 컬럼 조회
print(df.columns)
# payload를 드랍시킨 나머지 컬럼 조회
print(plain.columns)
print("=" * 50)

# [문제 2 · 한 단어] 빈칸을 채워보세요.
plain.write.mode("errorifexists").option("compression", "none").json(args.output + "/json")
# [문제 3 · 한 단어] 빈칸을 채워보세요.
plain.write.mode("errorifexists").option("compression", "snappy").parquet(args.output + "/parquet")

# JSON에는 원래 스키마를 적용해 두 형식의 행 수와 자료형을 비교한다.
# 예시: text_rows = session.read.schema(source.schema).json(folder + "/text")
#       column_rows = session.read.parquet(folder + "/columnar")
# [문제 4 · 여러 줄] JSON은 plain의 스키마를 지정하여 j로, Parquet은 q로 다시 읽는 두 줄을 작성해보세요. (2줄)
j = spark.read.schema(plain.schema).json(args.output + "/json")
q = spark.read.parquet(args.output + "/parquet")


print("input", plain.count(), "json", j.count(), "parquet", q.count())
print("json schema", j.schema.simpleString())
print("parquet schema", q.schema.simpleString())
spark.stop()