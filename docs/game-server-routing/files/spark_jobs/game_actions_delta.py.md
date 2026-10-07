# `spark_jobs/game_actions_delta.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Kafka 전달 기록을 event_id별 첫 확정 사실 Delta 테이블에 병합한다. 원문 수집 Parquet과 별도 상태를 갖는다.

## 소유 값과 입출력

필수 data-dir/bootstrap-servers; topic game.actions.v1; progress-output 선택. Delta lake/silver/game_actions; checkpoint checkpoints/game-actions-delta-v1; progress 기본 marts/progress-game-actions.json. schema는 6개 envelope 필드, payload는 payload_json 문자열로 별도 보존.

## 진입과 직접 호출 흐름

```text
실행
→ main
→ Kafka streaming projection
→ 중첩 save_unique의 foreachBatch MERGE
→ Delta 및 lastProgress 파일.
```

### `main` · `def main()`

```text
argparse 입력, data-dir resolve
→ Asia/Seoul/shuffle2 및 Delta extension/catalog SparkSession
→ Kafka earliest stream
→ from_json envelope와 raw_value/payload_json/Kafka 위치 투영
→ event_id 비null, schema1, 허용 event_type만 filter
→ 중첩 save_unique(batch,batch_id): event_id dropDuplicates, 빈 배치 return; persist; _delta_log가 없으면 errorifexists Delta 최초쓰기, 있으면 batch session temp view incoming_actions + MERGE(event_id 일치, NOT MATCHED INSERT *)
→ 고유 입력건수 출력, finally unpersist
→ foreachBatch/queryName/checkpoint/5초 trigger start
→ 완료 배치의 lastProgress를 .tmp/replace로 저장
→ KeyboardInterrupt 무시 후 query.stop/spark.stop. main 반환 None. 기존 동일 event_id의 내용을 갱신하거나 충돌 비교하지 않는다.
```

## 직접 연결 문서

- [`analytics/management/commands/run_game_delta.py`](../analytics/management/commands/run_game_delta.py.md)
- [`spark_jobs/game_batch.py`](game_batch.py.md)
- [`spark_jobs/dedup_game_actions.py`](dedup_game_actions.py.md)

## 현재 구현에서 확인할 점

save_unique는 main 안의 callback이므로 top-level inventory에는 별도 심볼이 없다. 배치 내 dropDuplicates는 같은 ID의 상충 내용에 대한 대표 행을 명시적으로 결정하지 않는다; 기존 Delta ID는 insert하지 않는다. 이는 conflict guard가 있는 정적 dedup_game_actions와 다른 계약이다.
