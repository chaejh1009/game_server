# `analytics/views.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

게시된 게임 집계·bounded Kafka 스냅샷·시간 창·전달 측정·부하 측정 파일을 JSON으로 조회한다. 요청에서 Spark나 Kafka 작업을 시작하거나 게임 상태를 수정하지 않는다.

## 소유 값과 입출력

DATA_DIR/marts/game-summary.json, windows.json, game-metrics.json; DATA_DIR/load/run-50.json. actions_snapshot만 DATA_DIR.parent/data-replay/actions/{marts/game-summary.json,raw/game-events.manifest.json}을 읽는다. ACTION_LABELS는 현재 표시 이름을 붙이는 용도다.

## 진입과 직접 호출 흐름

```text
config/urls.py / analytics/urls.py
→ 아래 핸들러
→ 파일 읽기·작은 표시용 변환
→ JsonResponse.
```

### `summary_view` · `def summary_view(request)`

```text
guard: @require_GET이 GET 이외 405; 비인증은 JSON login_required/401. DATA_DIR/marts/game-summary.json이 없으면 available=False, reason=summary_not_created/200
→ Path.read_text UTF-8
→ json.loads
→ {available: True, **summary} JsonResponse/200. 파일 내용의 스키마 검사·읽기 예외 처리는 이 함수에 없다.
```

### `actions_snapshot` · `def actions_snapshot(request)`

```text
guard: @login_required가 비인증 요청을 로그인 redirect로 처리; 별도 HTTP 메서드 제한 없음. 요약 또는 manifest가 없으면 available=False, reason=snapshot-or-summary-not-created, source_topic=game.actions.v1, summary=None/200
→ 두 JSON 파일 읽기
→ summary.by_action의 event_type에 ACTION_LABELS.get으로 현재 action_label 추가
→ manifest.topic/record_count/bounds와 작은 summary를 JsonResponse로 반환. source_kind=bounded-kafka-snapshot, label_source=current-display-map. 원문 value를 반환하지 않는다. JSON/필수키 예외는 여기서 잡지 않는다.
```

### `windows_view` · `def windows_view(request)`

```text
guard: @require_GET, 비인증 JSON401
→ DATA_DIR/marts/windows.json이 없으면 {available: False, windows: []}/200
→ UTF-8 JSON 읽기
→ {available: True, **result}/200. 창 계산·필터 재집계는 하지 않는다. 파일 해석 예외를 잡지 않는다.
```

### `metrics_snapshot` · `def metrics_snapshot(request)`

```text
guard: @login_required; 별도 메서드 제한 없음
→ DATA_DIR/marts/game-metrics.json이 없으면 {available: False, metrics: None}/200
→ JSON 파일을 읽어 {available: True, metrics: report}/200 반환. 값 재계산·Kafka commit 없음; 파일 해석 예외를 잡지 않는다.
```

### `load_snapshot` · `def load_snapshot(request)`

```text
guard: @login_required; 별도 메서드 제한 없음
→ DATA_DIR/load/run-50.json이 없으면 {available: False, load: None}/200
→ 허용 키 generated_at, measurement_started_at, profile, connected_success/peak, attempt/success/error_count, elapsed_seconds, success_per_second, rtt_sample_count/mean_ms/p95_ms만 투영
→ source.by_player를 room_id별 connected(int 합계), success_count로 집계·방 ID 정렬
→ {available: True, load: report}/200. 개별 player 원문은 반환하지 않는다; 파일·필수키 오류는 여기서 잡지 않는다.
```

## 직접 연결 문서

- [`analytics/urls.py`](urls.py.md)
- [`config/urls.py`](../config/urls.py.md)
- [`game/transforms.py`](../game/transforms.py.md)
- [`analytics/management/commands/collect_game_metrics.py`](management/commands/collect_game_metrics.py.md)
- [`spark_jobs/game_batch.py`](../spark_jobs/game_batch.py.md)
- [`spark_jobs/summarize_windows.py`](../spark_jobs/summarize_windows.py.md)
