# `spark_jobs/add_game_date.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

고유 Silver 사건의 UTC 시각으로 서울 달력 날짜를 추가하고 날짜별 Parquet으로 저장한다.

## 소유 값과 입출력

필수 --input/--output; 입력에 event_time/parsed_time 필요. event_date는 date; UTC Spark session, 달력 변환 Asia/Seoul.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark UTC
→ Silver Parquet
→ withColumn(event_date,to_date(from_utc_timestamp(parsed_time,Asia/Seoul)))
→ 시각/날짜 미리보기
→ errorifexists.partitionBy(event_date) 출력
→ 고정 UTC 자정 경계 세 표본을 createDataFrame/to_timestamp/from_utc_timestamp/to_date로 표시
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/dedup_game_actions.py`](dedup_game_actions.py.md)
- [`spark_jobs/build_game_daily.py`](build_game_daily.py.md)
- [`spark_jobs/layout_partition.py`](layout_partition.py.md)
