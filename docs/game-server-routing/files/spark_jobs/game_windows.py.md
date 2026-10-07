# `spark_jobs/game_windows.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Kafka 전달 레코드를 event-time 창으로 센다. event_id별 고유 사실 집계가 아니라 중복 전달을 포함할 수 있는 창 건수다.

## 소유 값과 입출력

필수 data-dir/bootstrap-servers; topic game.actions.v1; kind tumbling|sliding. watermark10초; tumbling 길이10초, sliding 길이20초/이동10초. 출력 lake/windows/<kind>; checkpoint checkpoints/windows/<kind>; progress marts/progress-windows-<kind>.json.

## 진입과 직접 호출 흐름

```text
main
→ Kafka stream
→ 사건 시각·종류 검증
→ watermark/window/count
→ 확정 창 append Parquet
→ progress 관찰.
```

### `main` · `def main()`

```text
argparse kind choices
→ Asia/Seoul/shuffle2 SparkSession
→ Kafka earliest
→ envelope+payload 해석, raw_value/Kafka 위치 보존
→ event_time to_timestamp
→ 시각/ID 비null, schema1, 허용종류 filter
→ withWatermark(10 seconds), window(duration,10 seconds)와 event_type별 count
→ kind/window_start/window_end/event_type/count 투영
→ append Parquet, queryName game-windows-kind, 전용checkpoint/5초trigger start
→ 새 lastProgress batchId마다 stdout + .tmp/replace progress 저장
→ KeyboardInterrupt 후 finally query.stop/spark.stop. 반환 None. dropDuplicates 호출은 없고 append 모드로 확정된 창만 파일에 도달한다.
```

## 직접 연결 문서

- [`analytics/management/commands/run_game_windows.py`](../analytics/management/commands/run_game_windows.py.md)
- [`spark_jobs/summarize_windows.py`](summarize_windows.py.md)

## 현재 구현에서 확인할 점

main 앞부분의 timed_actions와 초기 progress-windows-tumbling 경로는 후속 계산에 사용되지 않는다. 실제 groupBy는 actions.withWatermark를 다시 호출하고 실제 관찰 파일은 kind별 경로다.
