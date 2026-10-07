# `spark_jobs/layout_formats.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

같은 열 집합을 무압축 JSON과 Snappy Parquet으로 저장하고 재읽기 행수·스키마를 비교한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. 입력 Parquet에서 payload 제외; output/json 및 output/parquet은 errorifexists.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ df.drop(payload)=plain
→ 원본/선택 열 출력
→ JSON compression none, Parquet compression snappy 저장
→ JSON은 plain.schema 지정해 읽고 Parquet은 자체 schema로 읽음
→ 입력/양출력 count와 simpleString schema 출력
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/dedup_game_actions.py`](dedup_game_actions.py.md)
