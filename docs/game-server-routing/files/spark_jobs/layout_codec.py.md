# `spark_jobs/layout_codec.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

같은 Parquet 행을 Zstd와 Snappy로 저장·재읽기하며 실제 실행 시간을 측정한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. codec 순서 zstd,snappy; 각 output/<codec> errorifexists. 결과 codec,rows,write_seconds,read_seconds(JSON stdout).

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Parquet read
→ 각 codec마다 perf_counter 시작, 해당 compression 저장
→ 쓰기시간
→ 새 perf_counter, 재읽기와 count action
→ 읽기시간
→ 소수4자리 결과 append
→ JSON stdout
→ spark.stop. 결과 보고서 파일은 만들지 않는다.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/layout_formats.py`](layout_formats.py.md)
