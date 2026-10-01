import argparse
from pyspark.sql import SparkSession, functions as F

# 동일한 Parquet 입력과 새 출력 경로를 준비한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)
import json
import time

# Snappy와 Zstd로 각각 새 경로에 저장하고 쓰기·재읽기 시간을 잰다.
results = []
for codec in ["zstd", "snappy"]:
    target = args.output + "/" + codec
    # 예시: begin = time.perf_counter()
    # [문제 1 · 한 줄] 현재 코덱의 쓰기 경과 시간을 재기 위한 시작 시각을 기록하는 한 줄을 작성해보세요.
    started = time.perf_counter()
    # [문제 2 · 한 단어] 빈칸을 채워보세요.
    df.write.mode("errorifexists").option("compression", codec).parquet(target)
    write_seconds = time.perf_counter() - started
    started = time.perf_counter()
    restored = spark.read.parquet(target)

    # count로 읽기를 실제 실행한 뒤 경과 시간을 측정한다.
    # [문제 3 · 한 단어] 빈칸을 채워보세요.
    count = restored.count()
    read_seconds = time.perf_counter() - started

    # 압축 방식별 행 수와 두 시간을 모아 비교 결과로 출력한다.
    # 예시: measurements.append({
    #           "format": format_name, "seconds": round(elapsed, 3),
    #       })
    # [문제 4 · 여러 줄] 현재 codec와 count에 저장한 행 수를 codec·rows 키로와 소수 넷째 자리까지 반올림한 쓰기·읽기 시간을 결과 목록에 추가하는 코드를 작성해보세요. (5줄)
    results.append({
            "codec": codec, "rows": count,
            "write_seconds": round(write_seconds, 4),
            "read_seconds": round(read_seconds, 4),
        })
print(json.dumps(results, indent=2))
spark.stop()