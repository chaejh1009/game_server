# `spark_jobs/dedup_game_actions.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

정상 사건 전달에서 같은 event_id의 업무 내용 충돌을 거절하고 한 대표 전달을 선택한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. business=[schema_version,event_id,event_type,player_id,room_id,event_time,payload]. output=Silver Parquet(errorifexists).

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ accepted Parquet
→ payload map_entries를 sort_array로 정규화한 struct/to_json/sha2(256)로 body_hash
→ event_id별 countDistinct(body_hash)>1이면 conflicts 표시 후 ValueError
→ Window.partitionBy(event_id).orderBy(topic,partition,offset)
→ row_number==1 대표 행만 남기고 rn/body_hash/reason/value 제거
→ accepted/logical/duplicate_deliveries 건수 출력
→ Silver errorifexists 저장
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/check_game_quality.py`](check_game_quality.py.md)
- [`spark_jobs/add_game_date.py`](add_game_date.py.md)
- [`spark_jobs/game_actions_delta.py`](game_actions_delta.py.md)
