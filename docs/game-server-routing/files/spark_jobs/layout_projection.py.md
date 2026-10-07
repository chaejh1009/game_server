# `spark_jobs/layout_projection.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

필요한 열을 선택한 Parquet의 실행 계획·표본을 확인하고 새 출력에 저장한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. 실제 선택 열 event_date, room_id, event_type, player_id(4열). 출력 errorifexists.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Parquet read
→ select 4열
→ explain(formatted), show(10,truncate=False)
→ 새 Parquet 저장
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/add_game_date.py`](add_game_date.py.md)

## 현재 구현에서 확인할 점

현재 문제 주석은 세 열이라고 적지만 실행 select는 player_id를 포함한 네 열이다. 문서는 실제 코드를 따른다.
