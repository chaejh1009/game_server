import argparse
import time
from pyspark.sql import SparkSession, functions as F

# 동일한 입력을 읽어 태스크 수에 따른 파일 배치를 비교한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)
import json

# 2개·20개 파티션으로 각각 새 경로에 쓰고 실제 파일 수와 행 수를 확인한다.
result = []
# [문제 1 · 한 단어] 빈칸을 채워보세요.
for partitions in [2, 5, 20]:
    # perf_counter()를 활용해서, 개별 요소에 소요되는 시간이 얼마인지 구해보세요.
    start = time.perf_counter()

    path = args.output + "/tasks-" + str(partitions)
    # [문제 2 · 한 단어] 빈칸을 채워보세요.
    df.repartition(partitions).write.mode("overwrite").parquet(path)
    # 예시: restored_orders = session.read.parquet(output_path)
    # [문제 3 · 한 줄] 현재 파티션 설정으로 저장한 path를 다시 읽어 restored 표를 만드는 한 줄을 작성해보세요.
    restored = spark.read.parquet(path)
    # 예시: observations.append({
    #           "files": len(saved.inputFiles()), "records": saved.count(),
    #       })
    # [문제 4 · 여러 줄] 요청 태스크 수·실제 파일 수·복원한 행 수를 result 목록에 기록하는 코드를 작성해보세요. (5줄)
    result.append({
            "requested_tasks": partitions,
            "actual_files": len(restored.inputFiles()),
            "rows": restored.count(),
        })
    end = time.perf_counter()
    print("소요시간 :", (end - start))

print(json.dumps(result, indent=2))
spark.stop()