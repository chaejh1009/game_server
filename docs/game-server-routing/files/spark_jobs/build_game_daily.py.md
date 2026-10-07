# `spark_jobs/build_game_daily.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

날짜가 붙은 Silver를 날짜·방·종류별 Gold 행동 수와 활동 플레이어 수로 집계한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. group=(event_date,room_id,event_type); event_count=count(*), active_players=countDistinct(player_id); 날짜 partition 출력.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ dated Silver Parquet
→ groupBy/agg
→ event_count 내림차순 등으로 30행 표시
→ errorifexists.partitionBy(event_date) Gold 저장
→ source_count와 daily.sum(event_count) 비교(빈집계0)
→ 다르면 ValueError
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/add_game_date.py`](add_game_date.py.md)
- [`spark_jobs/publish_game_summary.py`](publish_game_summary.py.md)

## 현재 구현에서 확인할 점

보존 건수 검사는 출력 저장 뒤에 수행된다. 이 작업이 내보내는 Gold 스키마는 publish_game_summary가 읽는 Silver 스키마와 다르다; publish_game_summary의 입력으로 Gold를 바로 연결하지 않는다.
