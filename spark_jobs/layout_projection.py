import argparse
from pyspark.sql import SparkSession, functions as F

# 입출력 경로를 받고 UTC 세션에서 Silver Parquet을 읽는다.
# 예시: parser = argparse.ArgumentParser()
#       parser.add_argument("--source", required=True)
#       options = parser.parse_args()
# [문제 1 · 여러 줄] 필수 --input과 --output 인수를 등록하고 실제 명령행 값을 args로 읽는 코드를 작성해보세요. (4줄)
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()


spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
# [문제 2 · 한 단어] 빈칸을 채워보세요.
df = spark.read.parquet(args.input)

# 필요한 세 열만 선택해 실행 계획과 행을 확인하고 새 경로에 저장한다.
# errorifexists는 기존 결과 덮어쓰기를 막는다.
# 예시: chosen = orders.select("order_day", "store_id", "status")
# [문제 3 · 한 줄] event_date·room_id·event_type 세 열만 선택하는 한 줄을 작성해보세요.
selected = df.select("event_date", "room_id", "event_type", "player_id")

# [문제 4 · 한 단어] 빈칸을 채워보세요.
selected.explain("formatted")
selected.show(10, truncate=False)
# [문제 5 · 한 단어] 빈칸을 채워보세요.
selected.write.mode("errorifexists").parquet(args.output)
spark.stop()