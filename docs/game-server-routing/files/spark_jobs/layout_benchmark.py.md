# `spark_jobs/layout_benchmark.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Parquet 행수와 실제 파일수·총 bytes·평균 파일크기를 측정 보고서로 저장한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. report schema_version1/source_uri/rows/files/bytes/avg_file_bytes/master/generated_at. output은 직접 write_text JSON.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Parquet df
→ binaryFile recursiveFileLookup=true,pathGlobFilter=*.parquet로 path/length만 선택
→ count와 length sum
→ sum null은0, 파일0이면 평균0
→ df.count 및 sparkContext.master, UTC 시각 포함 report
→ 부모생성/write_text JSON 및 stdout
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/layout_compact.py`](layout_compact.py.md)

## 현재 구현에서 확인할 점

보고서는 임시파일 replace가 아닌 직접 쓰기다. 경과시간은 이 파일에서 측정하지 않으며 행수/파일수/bytes를 기록한다.
