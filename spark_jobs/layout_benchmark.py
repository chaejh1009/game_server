import argparse
from pyspark.sql import SparkSession, functions as F

# 측정할 Parquet 입력과 보고서 출력 경로를 받는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)
import json
from pathlib import Path
from datetime import datetime, timezone

# Parquet 파일의 경로·길이만 조회해 파일 수와 총 bytes를 집계한다.
# 예시: file_meta = session.read.format("binaryFile").option("recursiveFileLookup", "true").option(
#           "pathGlobFilter", "*.json"
#       ).load(source_path).select("path", "length")
# [문제 1 · 여러 줄] 하위 경로의 Parquet 파일만 binaryFile로 읽고 path·length 메타데이터 열을 선택하는 코드를 작성해보세요. (3줄)
meta = spark.read.format("binaryFile").option("recursiveFileLookup", "true").option(
    "pathGlobFilter", "*.parquet"
    ).load(args.input).select("path", "length")

# [문제 2 · 한 단어] 빈칸을 채워보세요.
sizes = meta.agg(F.count("*").alias("files"), F.sum("length").alias("bytes")).first()

# 파일이 없는지 있는지 측정한 후에 리포트를 작성하게 하기 위해 따로 빼두기
files = sizes["files"]
total_bytes = sizes["bytes"] or 0

# 파일이 없다면 0, 아니면 파일당 평균 bytes 계산
avg_file_bytes = total_bytes / files if files > 0 else 0

# 행 수와 파일 통계를 실제 Master·측정 시각과 함께 보고서에 담는다.
report = {
    "schema_version": 1, "source_uri": args.input,
    # 예시:     "records": source.count(), "files": stats["files"], "bytes": stats["bytes"] or 0,
    # [문제 3 · 한 줄] 원본 데이터 행 수와 측정한 파일 수·bytes를 report에 넣고 bytes가 없으면 0으로 두는 한 줄을 작성해보세요.
    "rows": df.count(), "files": files, "bytes": total_bytes, "avg_file_bytes":avg_file_bytes,
    # [문제 4 · 한 단어] 빈칸을 채워보세요.
    "master": spark.sparkContext.master,
    "generated_at": datetime.now(timezone.utc).isoformat(),
}

# 측정 보고서를 JSON으로 저장하고 출력한다.
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
spark.stop()