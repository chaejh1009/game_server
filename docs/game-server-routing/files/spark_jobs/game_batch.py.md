# `spark_jobs/game_batch.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

raw 또는 Delta 입력의 game event_id 고유 건수를 화면용 game-summary.json으로 게시한다.

## 소유 값과 입출력

필수 --data-dir; --source raw|delta 기본raw. raw=raw/game-events.jsonl; delta=lake/silver/game_actions; 결과 marts/game-summary.json. schema_version1, source 선택값, record_count/event_count/by_action/by_room. session Asia/Seoul, shuffle2.

## 진입과 직접 호출 흐름

```text
모듈 실행 즉시 argparse
→ SparkSession
→ source에 따라 schema JSON 또는 Delta read
→ schema/일부 사건 출력
→ record_count=전체행수
→ schema_version1 & event_id 비null filter
→ event_id/room_id/event_type 선택 후 event_id dropDuplicates
→ event_count, action별 전체그룹, room별 count내림차순 상위20 collect
→ UTC generated_at 포함 summary
→ game-summary.json.tmp 쓰기/replace
→ stdout
→ spark.stop(현재 코드에 두 번).
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`analytics/management/commands/summarize_game.py`](../analytics/management/commands/summarize_game.py.md)
- [`spark_jobs/game_actions_delta.py`](game_actions_delta.py.md)
- [`analytics/views.py`](../analytics/views.py.md)

## 현재 구현에서 확인할 점

이 파일은 함수 없이 import 시점에 실행된다. 허용 행동 종류·시간·상충 event_id 내용을 추가 검증하지 않으며 source=raw는 Kafka 원문 envelope가 아닌 DB 내보낸 사건 JSONL을 기대한다.
