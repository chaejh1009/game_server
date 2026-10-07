# `analytics/management/commands/collect_game_metrics.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

DB 확정 사실·발행 표식·Kafka 그룹 위치·마지막 Spark progress를 하나의 측정 snapshot으로 만든다. 레코드를 소비하거나 그룹 offset을 commit하지 않는다.

## 소유 값과 입출력

--seconds 기본60(1..3600); --topic 기본 game.events.v1; --group 기본 village-actions-v1. 결과 DATA_DIR/marts/game-metrics.json; progress 입력 marts/progress-game-actions.json.

## 진입과 직접 호출 흐름

```text
manage.py collect_game_metrics
→ Command
→ handle.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
parser.add_argument로 seconds(int), topic, group 등록
→ 파서에 옵션 저장; 반환 None.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
guard: seconds가 1..3600 아니면 CommandError
→ timezone.now로 [cutoff, now) 측정 구간 생성
→ KafkaConsumer(auto_commit=False, request_timeout_ms=15000)
→ partitions_for_topic/beginning_offsets/end_offsets/committed 조회; topic metadata 없으면 CommandError
→ commit이 retention 범위에 있을 때만 end-committed를 lag로 계산, 나머지는 None
→ finally consumer.close(autocommit=False)
→ GameEvent ORM에서 event_time 구간 건수·event_type/room_id별 Count, published_at 구간 건수, 전체 미발행 표식 건수/가장 오래된 나이 계산
→ progress 파일이 있으면 JSON의 id/runId/name/timestamp/batchId/numInputRows/inputRowsPerSecond/processedRowsPerSecond/eventTime만 투영
→ known_lag_sum 및 모든 partition 확인 여부 lag_complete 기록
→ .tmp 파일 쓰기 후 replace로 game-metrics.json 교체
→ stdout JSON. 명시적 반환 None; Kafka·JSON·DB 예외는 여기서 포괄 변환하지 않는다.
```

## 현재 구현에서 확인할 점

Kafka 지표 기본 topic은 game.events.v1이고 Spark actions 작업의 기본 topic은 game.actions.v1이다. 호출자가 선택한 topic/group의 위치이며 전체 처리량을 자동으로 같은 원천으로 맞추지 않는다.
