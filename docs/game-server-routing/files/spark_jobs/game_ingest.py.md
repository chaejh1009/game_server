# `spark_jobs/game_ingest.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Kafka game.actions 레코드의 전달 위치와 원문을 보존하며 valid/invalid/unsupported로 분류해 독립 Parquet에 append한다. 고유 사실 Delta를 만들거나 HTTP API를 제공하지 않는다.

## 소유 값과 입출력

ACTION_TYPES=player.moved/player.gathered/player.trained. EVENT_SCHEMA: schema_version int, event_id/event_type/room_id/event_time string, player_id long, payload(action_label string, version long). 출력 stream/game-actions-parquet; checkpoint checkpoints/game-ingest-v1; 관찰 marts/ingest-progress.json.

## 진입과 직접 호출 흐름

```text
스크립트 실행
→ main
→ parse_args
→ read_kafka
→ project_events
→ Parquet streaming writer
→ 마지막 관찰된 micro-batch progress JSON.
```

### `read_kafka` · `def read_kafka(spark, bootstrap_servers, topic, max_offsets)`

```text
입력 SparkSession/bootstrap/topic/max_offsets
→ readStream.format(kafka)
→ subscribe, startingOffsets=earliest, failOnDataLoss=true, maxOffsetsPerTrigger=str(max_offsets), groupIdPrefix=village-spark-ingest 설정
→ load()의 streaming DataFrame 반환. 함수 안에서 query를 시작하거나 commit하지 않는다; 재시작 offset은 query checkpoint가 결정한다.
```

### `project_events` · `def project_events(source)`

```text
입력 Kafka DataFrame
→ key/value를 문자열로, topic/partition/offset/timestamp를 kafka_* 열로 투영
→ from_json(raw_value, EVENT_SCHEMA)
→ 이벤트 필드와 payload_json/get_json_object 추출
→ try_to_timestamp(event_time)로 event_ts
→ event_id 비null·길이>0, player_id/room_id/event_ts/action_label 비null 필수 검사
→ 필수 실패 invalid; schema!=1 또는 허용 외 action unsupported; schema/action null invalid; 나머지 valid
→ current_timestamp ingested_at 추가
→ DataFrame 반환. 모든 분류의 원문/전달 위치를 보존하며 이 단계에서 dropDuplicates하지 않는다.
```

### `write_json_atomic` · `def write_json_atomic(target, document)`

```text
target을 Path로 변환, 부모 생성
→ 같은 폴더 NamedTemporaryFile(delete=False)에 JSON(UTF-8, indent2)+개행
→ flush와 os.fsync
→ os.replace로 최종 파일 교체
→ finally 남은 임시 파일 unlink. 반환 None; 실패는 호출자에게 전파하고 기존 최종 파일을 교체 전까지 보존한다.
```

### `parse_args` · `def parse_args()`

```text
필수 data-dir/bootstrap-servers; topic game.actions.v1; mode continuous|available-now; max-offsets1000; trigger-seconds5 등록
→ parse_args
→ rate/interval이 1 미만이면 parser.error
→ Namespace 반환.
```

### `main` · `def main()`

```text
parse_args
→ data-dir resolve, UTC/shuffle2 SparkSession
→ read_kafka/project_events
→ printSchema
→ append Parquet writer와 별도 checkpoint, queryName=village-game-ingest-v1 설정
→ availableNow 또는 processingTime trigger
→ start
→ 활성 query.lastProgress의 batchId가 바뀔 때만 write_json_atomic으로 ingest-progress 관찰값 저장 및 작은 stdout
→ awaitTermination 반복. KeyboardInterrupt는 보존 안내; finally 활성 query.stop와 spark.stop. 반환 None; 출력·checkpoint를 삭제하지 않는다.
```

## 직접 연결 문서

- [`analytics/management/commands/run_game_ingest.py`](../analytics/management/commands/run_game_ingest.py.md)
- [`spark_jobs/summarize_ingest.py`](summarize_ingest.py.md)
