# 분석 서버 라우팅과 데이터 원천

[전체 라우팅 목차](README.md)

analytics 앱은 게임 확정 사실을 저장하는 앱이 아니다. management command가 Spark 작업이나 관찰 작업을 실행하고 결과 파일을 만든다. HTTP 핸들러는 그 결과를 읽어 접속기에 전달한다. 파일별 문서는 `files/<프로젝트 상대경로>.md`와 대응한다.

이 문서의 경로는 Django `settings.DATA_DIR`를 기준으로 한다. 값은 코드의 설정 참조만 기록하며 로컬 `.env` 파일을 읽거나 설정값을 복제하지 않는다. tests, test_ 파일, migrations, 빈 `__init__.py`는 범위에서 제외했다.

## HTTP 조회 진입점

최상위 연결은 [`config/urls.py`](files/config/urls.py.md), 앱 내부 연결은 [`analytics/urls.py`](files/analytics/urls.py.md)다. 조회는 저장된 파일을 읽으며 Spark 실행·Kafka 수집·게임 상태 변경을 요청하지 않는다.

| 경로 | 코드가 허용하는 메서드와 인증 | 핸들러 | 읽는 파일·반환 경계 |
|---|---|---|---|
| `/api/analytics/` | GET만 허용. 비인증 JSON401 | [`summary_view(request)`](files/analytics/views.py.md) | `marts/game-summary.json`; 미생성 available=false/200 |
| `/api/analytics/ingest/` | GET만 허용. 비인증 JSON401 | [`ingest_summary_view(request)`](files/analytics/ingest_views.py.md) | `marts/stream-summary.json`; 미생성200, 기본 계약·읽기 오류503, 성공 no-store |
| `/api/analytics/windows/` | GET만 허용. 비인증 JSON401 | [`windows_view(request)`](files/analytics/views.py.md) | `marts/windows.json`; 미생성 available=false/windows=[] |
| `/api/analytics/actions/` | `login_required`; 별도 메서드 제한 없음 | [`actions_snapshot(request)`](files/analytics/views.py.md) | `DATA_DIR.parent/data-replay/actions` 아래 bounded snapshot manifest·summary. 현재 행동 표시 이름만 추가 |
| `/api/analytics/metrics/` | `login_required`; 별도 메서드 제한 없음 | [`metrics_snapshot(request)`](files/analytics/views.py.md) | `marts/game-metrics.json`; 미생성 metrics=null |
| `/api/analytics/load/` | `login_required`; 별도 메서드 제한 없음 | [`load_snapshot(request)`](files/analytics/views.py.md) | `load/run-50.json`; 허용 측정값 및 방별 집계만 반환, 개별 플레이어 목록 제외 |

`login_required` 핸들러의 비인증 응답은 기본 로그인 redirect다. 세 GET 전용 핸들러의 JSON401과 구별한다. `ingest_summary_view` 외 핸들러는 JSON 해석·필수키 오류를 자체 503 응답으로 변환하지 않는다.

## 명령 → Spark → 파일 → 조회

```text
게임 확정 GameEvent
  ├─ 기존 DB export → raw/game-events.jsonl
  │    → summarize_game --source raw → game_batch.py
  │    → marts/game-summary.json → GET /api/analytics/
  └─ 기존 publisher/행동 변환기 → Kafka game.actions.v1
       ├─ run_game_ingest → game_ingest.py
       │    → stream/game-actions-parquet (모든 분류의 전달 레코드)
       │    → summarize_ingest → summarize_ingest.py
       │    → marts/stream-summary.json → GET /api/analytics/ingest/
       │    └─ 선택 사건 evidence/day15/event-<UUID>.json (HTTP 원문 응답 아님)
       ├─ run_game_delta → game_actions_delta.py
       │    → lake/silver/game_actions (event_id별 insert-only Delta 사실)
       │    → summarize_game --source delta → game_batch.py
       │    → marts/game-summary.json → GET /api/analytics/
       └─ run_game_windows → game_windows.py
            → lake/windows/{tumbling,sliding} (확정 창 Parquet)
            → summarize_windows → summarize_windows.py
            → marts/windows.json → GET /api/analytics/windows/

collect_game_metrics
  → GameEvent ORM + Kafka 그룹 offset + progress-game-actions.json
  → marts/game-metrics.json → GET /api/analytics/metrics/

외부 부하 측정 도구 → load/run-50.json → GET /api/analytics/load/
bounded actions snapshot + 그 snapshot의 summary
  → DATA_DIR.parent/data-replay/actions/{raw,marts}
  → GET /api/analytics/actions/
```

[`summarize_game`](files/analytics/management/commands/summarize_game.py.md)의 raw·delta 선택은 같은 `game-summary.json` 게시 위치를 교체한다. 조회 화면의 숫자를 비교할 때 응답의 `source`도 함께 확인해야 한다. [`summarize_ingest`](files/analytics/management/commands/summarize_ingest.py.md)는 별도 `stream-summary.json`을 만든다.

## 원천, checkpoint, 관찰 파일

| 종류 | 경로 | 의미·소유자 |
|---|---|---|
| DB export 원천 | `raw/game-events.jsonl` | [`game_batch.py`](files/spark_jobs/game_batch.py.md)의 source=raw 입력. Kafka topic/key/value 바깥 envelope가 아닌 사건 JSONL |
| 전달 원천 | `stream/game-actions-parquet` | [`game_ingest.py`](files/spark_jobs/game_ingest.py.md)가 append한 Kafka 전달 레코드, raw_value와 Kafka 위치·분류 보존 |
| 고유 사실 원천 | `lake/silver/game_actions` | [`game_actions_delta.py`](files/spark_jobs/game_actions_delta.py.md)의 Delta 테이블. `_delta_log`는 테이블 트랜잭션 기록 |
| 확정 창 결과 | `lake/windows/<kind>` | [`game_windows.py`](files/spark_jobs/game_windows.py.md)의 append 출력. 완료된 event-time 창 건수 |
| 수집 재개 상태 | `checkpoints/game-ingest-v1` | 수집 query의 offset/commit 등 Spark 재개 정보. 사건 파일이나 조회 요약이 아님 |
| Delta 재개 상태 | `checkpoints/game-actions-delta-v1` | Delta streaming query 전용 checkpoint. Delta 테이블 `_delta_log`와 다른 경로 |
| 창 재개 상태 | `checkpoints/windows/<kind>` | 창 query의 offset·상태·watermark 재개 정보. 조회용 창 Parquet과 별도 |
| 수집 관찰값 | `marts/ingest-progress.json` | 마지막 관찰 완료 micro-batch의 입력건수·처리율·sources. 전체 수집 통계가 아님 |
| Delta 관찰값 | `marts/progress-game-actions.json` | Delta query lastProgress. [`collect_game_metrics`](files/analytics/management/commands/collect_game_metrics.py.md)가 일부 키를 읽음 |
| 창 관찰값 | `marts/progress-windows-<kind>.json` | 창 query lastProgress, eventTime/stateOperators 포함. 창 목록 자체가 아님 |
| 조회 결과 | `marts/game-summary.json`, `stream-summary.json`, `windows.json`, `game-metrics.json` | 각 게시 작업이 생성한 작은 JSON. API는 이 파일을 조회 |
| 환경 관찰 | `evidence/day15/environment.json` | [`capture_ingest_environment`](files/analytics/management/commands/capture_ingest_environment.py.md)의 설정 기록. `spark_executed=false` |
| 선택 사건 증거 | `evidence/day15/event-<UUID>.json` | 수집 Parquet 내 최대20개 상세 전달. raw_value가 포함되며 ingest HTTP 응답과 분리 |

처음 Kafka를 읽을 때의 `startingOffsets=earliest`와 query 재시작 위치를 구별한다. 기존 checkpoint를 사용하는 재시작 위치는 checkpoint 상태를 따른다. 수집·Delta·창 query는 각각 다른 checkpoint를 쓰며 코드가 종료 시 이를 삭제하지 않는다.

## 주요 스키마와 건수 의미

| 데이터 | 주요 필드·검사 | 건수의 단위 |
|---|---|---|
| Kafka 행동 envelope | `schema_version`, `event_id`, `event_type`, `player_id`, `room_id`, `event_time`, `payload`; 허용 종류 moved/gathered/trained | 사건의 업무 ID는 event_id, 전달 위치는 topic/partition/offset |
| 독립 수집 Parquet | envelope 투영 + `raw_value`, `payload_json`, `kafka_key/topic/partition/offset/timestamp`, `event_ts`, `parse_status`, `ingested_at` | 같은 event_id가 여러 전달로 남을 수 있음 |
| 수집 요약 | `schema_version=1`, `source=kafka-parquet`, `basis=all-collected-records`; record/valid/invalid/unsupported/event/duplicate_count, action·room 그룹, 시각범위, sample IDs | record_count=전체 전달행; event_count=valid 중 고유 event_id; duplicate_record_count=valid-event |
| Delta 사실 | envelope 6필드 + raw_value/payload_json/Kafka 위치; schema1/허용종류/event_id 비null만 stream filter | 최초 event_id별 1행. 기존 ID 갱신·업무 내용 충돌 검사는 없음 |
| 게임 화면 요약 | `schema_version=1`, `generated_at`, `source=raw|delta`, `record_count`, `event_count`, `by_action`, `by_room` | 선택 원천의 행수와 schema1/ID비null 고유 사건 수. 방그룹은 상위20 |
| 확정 창 | `kind`, `window_start`, `window_end`, `event_type`, `count` | 전달 레코드 건수. 고유 사건 수가 아님; sliding은 한 레코드가 겹친 창에 포함 가능 |
| 창 조회 JSON | `generated_at`, `windows` | 종류별 최신 최대5/10/20개 창 행. 생성 시각은 사건 시각·watermark와 별도 |
| 전달 측정 JSON | 측정구간/확정건수/최근발행/미발행표식/방·행동별건수, Kafka partitions/lag_complete, Spark progress 일부 | DB 구간 건수, publisher 표식, 특정 Kafka topic/group 위치, Spark 관찰시각을 각각 유지 |
| 부하 조회 JSON | 허용 연결·명령·처리율·RTT 필드와 by_room | 저장된 측정 결과를 투영. 게임 DB 플레이어 수로 연결수를 합성하지 않음 |

수집 요약의 schema_version은 정수 `1`이다. Day23 광고 사건의 문자열 계약 `ad-event/v1`과 혼용하지 않는다. `generated_at`, `event_time`, `ingested_at`, progress timestamp는 각각 게시·발생·수집·관찰 시각이다.

## 정적 Bronze → Silver → Gold 실험

아래 Spark 파일은 함수 선언 없이 모듈 최상위에서 argparse와 Spark I/O를 실행한다. 도구 실행 파일로 다루며 일반 helper 모듈처럼 import하지 않는다. 입출력은 대부분 필수 `--input`, `--output` 인수로 정한다.

```text
bounded Kafka snapshot JSON(topic/key/value/partition/offset)
  → bronze_preview.py (미리보기만)
  → parse_game_bronze.py (value 해석·펼침 Parquet)
  → check_game_quality.py (accepted / quarantine)
  → dedup_game_actions.py (내용 충돌 거절·대표 전달 선택)
  → add_game_date.py (서울 달력 event_date)
  ├─ build_game_daily.py (날짜/방/행동 Gold)
  └─ publish_game_summary.py (개별 Silver로 화면용 JSON)
```

[`dedup_game_actions.py`](files/spark_jobs/dedup_game_actions.py.md)는 같은 ID의 업무 지문 충돌을 거절한다. 스트리밍 Delta 작업은 기존 ID에 insert하지 않는 계약이며 같은 충돌 검사를 수행하지 않는다. 두 방식의 차이를 문서에 유지한다.

Gold 일별 집계를 [`publish_game_summary.py`](files/spark_jobs/publish_game_summary.py.md)의 입력으로 직접 넣지 않는다. 이 게시 파일은 개별 Silver를 count하며 `dataset_version=capture-001`을 추가하고 `source`·`record_count`는 넣지 않는다. `game_batch.py`의 요약과 JSON 필드 구성이 다르다.

## 파일별 책임 색인

| 실제 파일 | 문서 | 책임 |
|---|---|---|
| `analytics/admin.py` | [문서](files/analytics/admin.py.md) | 모델 등록 없는 admin 자리 |
| `analytics/apps.py` | [문서](files/analytics/apps.py.md) | analytics AppConfig |
| `analytics/models.py` | [문서](files/analytics/models.py.md) | 모델 선언 없는 자리 |
| `analytics/urls.py` | [문서](files/analytics/urls.py.md) | summary/ingest/windows URL |
| `analytics/views.py` | [문서](files/analytics/views.py.md) | 게임·창·측정 snapshot 조회 |
| `analytics/ingest_views.py` | [문서](files/analytics/ingest_views.py.md) | 수집 요약 기본 계약 검사 |
| `analytics/management/commands/capture_ingest_environment.py` | [문서](files/analytics/management/commands/capture_ingest_environment.py.md) | 실행 전 환경 관찰 |
| `analytics/management/commands/collect_game_metrics.py` | [문서](files/analytics/management/commands/collect_game_metrics.py.md) | DB/Kafka/progress 측정 |
| `analytics/management/commands/publish_window_demo.py` | [문서](files/analytics/management/commands/publish_window_demo.py.md) | 별도 topic에 합성 창 자료 발행 |
| `analytics/management/commands/run_game_delta.py` | [문서](files/analytics/management/commands/run_game_delta.py.md) | Delta query 제출 |
| `analytics/management/commands/run_game_ingest.py` | [문서](files/analytics/management/commands/run_game_ingest.py.md) | 독립 Parquet 수집 제출 |
| `analytics/management/commands/run_game_windows.py` | [문서](files/analytics/management/commands/run_game_windows.py.md) | 창 query 제출 |
| `analytics/management/commands/summarize_game.py` | [문서](files/analytics/management/commands/summarize_game.py.md) | raw/delta 게임 요약 제출 |
| `analytics/management/commands/summarize_ingest.py` | [문서](files/analytics/management/commands/summarize_ingest.py.md) | 수집 전용 요약 제출 |
| `analytics/management/commands/summarize_windows.py` | [문서](files/analytics/management/commands/summarize_windows.py.md) | 창 요약 제출 |
| `spark_jobs/game_ingest.py` | [문서](files/spark_jobs/game_ingest.py.md) | Kafka 전달 분류·Parquet 보존 |
| `spark_jobs/game_actions_delta.py` | [문서](files/spark_jobs/game_actions_delta.py.md) | event_id별 Delta MERGE |
| `spark_jobs/game_windows.py` | [문서](files/spark_jobs/game_windows.py.md) | event-time 확정 창 |
| `spark_jobs/game_batch.py` | [문서](files/spark_jobs/game_batch.py.md) | raw/delta 화면 요약 |
| `spark_jobs/summarize_ingest.py` | [문서](files/spark_jobs/summarize_ingest.py.md) | 전달·고유 사건·선택 evidence |
| `spark_jobs/summarize_windows.py` | [문서](files/spark_jobs/summarize_windows.py.md) | 확정 창 일부 게시 |
| `spark_jobs/bronze_preview.py` | [문서](files/spark_jobs/bronze_preview.py.md) | snapshot 전달 위치 관찰 |
| `spark_jobs/parse_game_bronze.py` | [문서](files/spark_jobs/parse_game_bronze.py.md) | envelope 펼침 |
| `spark_jobs/check_game_quality.py` | [문서](files/spark_jobs/check_game_quality.py.md) | 정상·격리 구분 |
| `spark_jobs/dedup_game_actions.py` | [문서](files/spark_jobs/dedup_game_actions.py.md) | 충돌 거절·대표 전달 선택 |
| `spark_jobs/add_game_date.py` | [문서](files/spark_jobs/add_game_date.py.md) | 서울 달력 날짜 추가 |
| `spark_jobs/build_game_daily.py` | [문서](files/spark_jobs/build_game_daily.py.md) | 날짜·방·행동 Gold |
| `spark_jobs/publish_game_summary.py` | [문서](files/spark_jobs/publish_game_summary.py.md) | Silver 화면 요약 게시 |
| `spark_jobs/layout_formats.py` | [문서](files/spark_jobs/layout_formats.py.md) | JSON/Parquet 비교 |
| `spark_jobs/layout_codec.py` | [문서](files/spark_jobs/layout_codec.py.md) | Zstd/Snappy 측정 |
| `spark_jobs/layout_projection.py` | [문서](files/spark_jobs/layout_projection.py.md) | 실제4열 projection |
| `spark_jobs/layout_partition.py` | [문서](files/spark_jobs/layout_partition.py.md) | 날짜 partition 읽기 관찰 |
| `spark_jobs/layout_smallfiles.py` | [문서](files/spark_jobs/layout_smallfiles.py.md) | 2/5/20 partition 파일 비교 |
| `spark_jobs/layout_compact.py` | [문서](files/spark_jobs/layout_compact.py.md) | coalesce3·행 차이 검사 |
| `spark_jobs/layout_benchmark.py` | [문서](files/spark_jobs/layout_benchmark.py.md) | 행수·파일수·bytes 보고서 |

## 현재 구현에서 확인할 점

- `collect_game_metrics`의 기본 Kafka topic은 `game.events.v1`, Spark actions 작업의 기본 topic은 `game.actions.v1`이다. 각각의 측정 원천을 명시한다.
- `layout_projection`은 주석과 달리 player_id까지 4열, `layout_partition`의 날짜 표본은 실제5개, `layout_smallfiles`는 실제2/5/20을 비교한다.
- `layout_compact`는 실제 coalesce(3)이며 역방향 비교가 subtract다. 양방향 exceptAll과 같은 중복 보존 검증이라고 설명하지 않는다.
- 일부 정적 스크립트는 저장 후 건수·행 차이를 검증한다. 실패 메시지가 이미 만든 출력 경로를 자동으로 지우지는 않는다.

위 내용은 현재 코드의 책임과 차이를 기록한 것이며 코드 수정 제안이나 실행 검증 결과를 뜻하지 않는다. 문서 작성에서는 AST inventory로 선언과 서명을 대조했고 Spark/Kafka/DB 작업은 실행하지 않았다.
