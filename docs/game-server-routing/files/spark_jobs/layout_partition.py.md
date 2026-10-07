# `spark_jobs/layout_partition.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

날짜 partition 저장 후 한 날짜 조건의 읽기 계획을 관찰한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. 날짜 표본 distinct/orderBy/limit(5); output은 partitionBy(event_date), errorifexists.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Parquet read
→ event_date distinct 정렬 후 최대5 collect
→ 비면 ValueError("dates has no dates")
→ 전체 df 날짜partition 저장
→ 다시 읽어 첫 날짜 chosen과 같은 행 filter
→ explain(formatted), 날짜별 count 표시, chosen 출력
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/add_game_date.py`](add_game_date.py.md)

## 현재 구현에서 확인할 점

현재 설명 주석은 최대 열 개이나 실제 limit은 5다. 표본의 첫 날짜를 선택하며 날짜 전체 목록을 driver로 수집하지 않는다.
