# `spark_jobs/summarize_ingest.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

독립 수집 Parquet에서 전달 수·고유 valid 사건 수·중복 수를 계산하고 작은 HTTP 조회용 요약을 게시한다. 선택 event_id의 원문 evidence는 별도 파일로 남긴다.

## 소유 값과 입출력

필수 data-dir; 선택 event-id UUID. 입력 stream/game-actions-parquet; 출력 marts/stream-summary.json(schema_version1, source=kafka-parquet, basis=all-collected-records); evidence/day15/event-<UUID>.json. 그룹별 최대1000, sample_event_ids 최대10, evidence matches 최대20.

## 진입과 직접 호출 흐름

```text
main
→ 수집 Parquet cache
→ valid 사건 event_id dedup
→ small_groups
→ game_ingest.write_json_atomic
→ stream-summary/evidence.
```

### `small_groups` · `def small_groups(frame, column)`

```text
입력 frame/column
→ groupBy(column).count().orderBy(column).limit(1001).collect
→ 1000그룹 초과이면 ValueError
→ [{column: 값, count: int}] 목록 반환. 전체 원문을 driver로 가져오지 않는다.
```

### `main` · `def main()`

```text
event-id UUID 정규화; source_path가 디렉터리 아니면 ValueError
→ UTC/shuffle2 SparkSession
→ 수집 rows.cache
→ valid filter 후 event_id dropDuplicates/cache
→ 상태별 전달건수, 고유 event_count, duplicate=valid_count-event_count, 최소/최대 event_ts, sample10 계산
→ small_groups(action/room)
→ write_json_atomic(stream-summary)
→ 선택 ID 있으면 전체 rows에서 matching count, Kafka 위치순 최대20 details(raw_value 포함) 수집 후 evidence JSON 별도쓰기
→ finally unique/rows unpersist 및 spark.stop. 반환 None. evidence는 전체 수집 내 일치 자료이지 Kafka 전체 이력이나 API 응답이 아니다.
```

## 직접 연결 문서

- [`spark_jobs/game_ingest.py`](game_ingest.py.md)
- [`analytics/management/commands/summarize_ingest.py`](../analytics/management/commands/summarize_ingest.py.md)
- [`analytics/ingest_views.py`](../analytics/ingest_views.py.md)
