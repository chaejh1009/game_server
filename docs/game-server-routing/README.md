# Game server routing

이 문서는 현재 게임 서버의 코드 탐색 진입점이다. `game_client`의 라우팅 문서처럼 파일별 책임·함수 서명·직접 호출 경계를 연결한다. HTTP·WebSocket 처리, 광고 서버 중계, 관리 명령, Kafka·Spark 분석 작업을 실제 코드 기준으로 기록한다.

## 범위

직접 유지보수하는 런타임 Python **85파일·139개 클래스/함수/메서드**를 다룬다. 각 파일은 `files/<프로젝트 상대경로>.md` 하나에 대응한다. `manage.py`, `config`, `game`, `analytics`, `spark_jobs`, `tools`를 포함한다.

테스트(`tests.py`, `test_*.py`), migrations, 빈 `__init__.py`, 교시별 독립 연습인 `tools/basics/**`, 가상환경·캐시·DB·데이터 산출물·`.env`는 제외한다. 템플릿·정적 파일은 소비하는 view의 문서에서 참조한다. 설정은 변수명과 경로 해석 규칙으로 설명하고 비밀값은 기록하지 않는다.

## 계층별 호출 구조

```text
manage.py -> Django 관리 명령 / 개발 서버
config.asgi.application
  HTTP -> Django middleware -> config.urls -> game.urls / analytics.urls
    game.views -> game.services -> Player + GameEvent (같은 transaction)
    game.ad_events / game.views.ad_decision -> game.ad_gateway -> ad_server HTTP
    analytics.views / ingest_views -> 이미 게시된 작은 JSON 파일
  WebSocket -> origin 검사 -> session 인증 -> game.routing -> PlayConsumer
    -> game.services.apply_command -> DB -> 방 state/snapshot broadcast
config.wsgi.application -> Django HTTP 처리

game 관리 명령 -> DB export / Kafka outbox 발행 / 사실→행동 변환 / 고정 범위 snapshot
analytics 관리 명령 -> spark-submit -> spark_jobs -> Parquet/Delta/창 결과 -> 게시 JSON
tools -> 표본 검증 / Bronze 보존·사본 / 전이 인계 / 실제 WS 부하 측정
```

- [게임·광고·관리 명령 상세 흐름](core-overview.md)
- [분석 API·Spark·원천·checkpoint·스키마 상세 흐름](analytics-overview.md)
- [도구 파일 목차](tools-overview.md)

## HTTP 경로 → 핸들러

경로는 루트 기준이며 trailing slash를 포함한다. URL resolver는 method로 후보를 고르지 않는다. 먼저 일치한 경로의 뷰를 고른 뒤 해당 뷰가 method를 검사한다.

| URL | 현재 handler | method·인증 | 결과 |
| --- | --- | --- | --- |
| `/play/` | [views.play](files/game/views.py.md) | login_required; 명시 method 제한 없음 | game/play.html; 미로그인 redirect |
| `/api/player/` | views.player_view | GET, session user | state JSON; 미로그인401 |
| `/api/delivery/` | views.delivery_view | GET, session user | 현재 사용자의 mysql-outbox 전체/미발행 수 |
| `/api/history/` | views.history | login_required; 명시 method 제한 없음 | 현재 사용자 최신20개 사실; 미로그인 redirect |
| `/api/auth/csrf/` | views.csrf_view | GET, 로그인 불필요 | csrfToken JSON·cookie |
| `/api/auth/login/` | views.api_login | POST JSON·CSRF | session 로그인; 실패400/401 |
| `/ads-preview/` | views.ad_preview | GET, 로그인 불필요 | 광고 확인 HTML |
| `/api/ads/decision/` | views.ad_decision | POST JSON·session·CSRF | 선택 또는 빈 광고 dict; 오류400/401/404/503 |
| `/api/ads/events/` | [ad_events.ad_event](files/game/ad_events.py.md) | POST JSON·session·CSRF | event_id/event_type/created; 뷰 오류400/401/409/503, method405·CSRF403 |
| `/accounts/…` | Django auth.urls include | Django 내장 뷰 계약 | 로그인·로그아웃 등 |
| `/admin/…` | admin.site.urls | Django admin 계약 | game/admin.py는 현재 모델 등록 없음 |

`config.urls`에서 빈 prefix `include("game.urls")`가 루트의 `path("api/ads/decision/", ad_gateway.decision)`보다 먼저 등록되어 있다. 따라서 GET `/api/ads/decision/`도 **views.ad_decision으로 resolve되어 405**다. 뒤의 GET용 `ad_gateway.decision`은 현재 같은 경로에서 도달하지 않는다. `game:ad-decision`과 루트 `ad-decision`의 reverse 이름 차이가 실제 요청의 우선순위를 바꾸지 않는다. 이 문서는 route를 고치지 않고 현재 상태를 기록한다.

최상위에는 `/api/analytics/` include와 그 뒤 actions/metrics/load 직접 경로도 있다. 하위 include가 먼저 검사된다. analytics 실제 route·함수 계약은 [분석 흐름 문서](analytics-overview.md)에 있다.

### 분석 조회 경로

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

## WebSocket과 핵심 계약

- `/ws/play/` → `game.consumers.PlayConsumer`. 인증 세션과 origin을 확인하고 방별 state/snapshot을 전달한다. 이동·채집·수련은 `game.services.apply_command`가 검증한다.
- 성공한 명령의 Player 변경과 GameEvent 생성은 하나의 transaction이다. 같은 Player의 같은 command_id는 새 사실을 만들지 않는다. ONLINE과 InMemoryChannelLayer는 현재 프로세스 안에서만 공유된다.
- 광고 이벤트 경로의 reverse 이름은 `game:ad-events`다. CSRF 검사는 뷰 진입 전에 수행될 수 있으며, 뷰에서는 POST 제한 → 로그인 → Player → JSON 입력 → gateway 순서로 검사한다.
- 클라이언트 광고 이벤트 입력은 decision_id와 event_type 두 값이다. subject는 게임 서버가 로그인 Player의 pk로 만든 `{media_id, subject_id}` 객체다. 게임 서버는 선택이나 이미지 다운로드만으로 노출을 생성하지 않는다.
- GameEvent의 event_id는 사실 식별자이고 Kafka topic/partition/offset은 전달 위치다. Outbox ack 이후 published_at 기록 전 장애로 재전달이 생길 수 있다.
- 조회용 분석 JSON, 원천 Parquet/Delta, Spark checkpoint, lastProgress는 각각 다른 경계다. HTTP 조회는 저장된 결과만 읽으며 Spark 작업을 실행하지 않는다.
- 현재 광고 서버에 없는 export/report/delivery 구현이나 교안 다운로드 자산을 이미 연결된 서버 기능으로 기재하지 않는다.

## 파일별 책임과 상세 문서

### 실행·설정·게임 처리

| 실제 파일 | 라우팅 문서 | 책임 |
|---|---|---|
| `config/asgi.py` | [문서](files/config/asgi.py.md) | HTTP와 WebSocket을 나누는 ASGI 조립점이다. Django 초기화를 먼저 끝내고 game.routing을 가져온다. |
| `config/settings.py` | [문서](files/config/settings.py.md) | Django·Channels·MySQL·Kafka·Spark·광고 gateway 설정의 조립점이다. 게임 로직과 인증 키를 클라이언트로 내보내지 않는다. |
| `config/urls.py` | [문서](files/config/urls.py.md) | 최상위 HTTP 라우터다. urlpatterns는 위에서부터 경로를 찾으며 뷰의 허용 HTTP method는 URL 매칭 뒤 검사한다. |
| `config/wsgi.py` | [문서](files/config/wsgi.py.md) | HTTP 전용 WSGI 진입점이다. WebSocket 라우터를 조립하지 않는다. |
| `game/ad_events.py` | [문서](files/game/ad_events.py.md) | 인증된 게임 사용자의 광고 이벤트 POST bridge다. 요청 subject를 받지 않고 Player identity를 gateway에 넘긴다. 기존 CSRF 정책을 그대로 따른다. |
| `game/ad_gateway.py` | [문서](files/game/ad_gateway.py.md) | 게임 인증 사용자·Player를 매체 subject로 바꾸고 서버 간 광고 HTTP 요청에 인증 header를 붙인다. 게임 cookie·비밀번호를 광고 서버에 넘기지 않는다. |
| `game/admin.py` | [문서](files/game/admin.py.md) | Django admin 모듈 자리다. 현재 django.contrib.admin을 import하지만 모델을 register하지 않는다. |
| `game/apps.py` | [문서](files/game/apps.py.md) | INSTALLED_APPS의 game 앱 메타데이터다. HTTP/WS 핸들러나 ready hook은 정의하지 않는다. |
| `game/consumers.py` | [문서](files/game/consumers.py.md) | 인증 세션 WebSocket의 연결·방 broadcast·수신 빈도 제한을 소유한다. 동기 ORM/게임 서비스 호출은 database_sync_to_async로 감싸 비동기 소비자와 분리한다. |
| `game/models.py` | [문서](files/game/models.py.md) | 현재 플레이 상태와 확정 사실 Outbox의 영속 모델이다. 광고 decision/event는 이 MySQL 모델에 저장하지 않는다. |
| `game/routing.py` | [문서](files/game/routing.py.md) | WebSocket 경로만 등록한다. HTTP urlpatterns와 구분되며 ASGI URLRouter가 사용한다. |
| `game/services.py` | [문서](files/game/services.py.md) | 게임 규칙, 명령 멱등 처리, 전이 데이터, Player와 GameEvent의 원자적 저장을 소유한다. 네트워크 전송과 광고 선택은 하지 않는다. |
| `game/transforms.py` | [문서](files/game/transforms.py.md) | Kafka 사실 envelope을 검증하고 허용 게임 행동에 한국어 표시 이름을 붙이는 순수 변환 모듈이다. consumer group·offset·전송은 소유하지 않는다. |
| `game/urls.py` | [문서](files/game/urls.py.md) | 인증된 게임 HTTP와 광고 bridge의 경로를 등록한다. app_name은 game이며 실제 인증·CSRF·method 판정은 뷰와 middleware가 수행한다. |
| `game/views.py` | [문서](files/game/views.py.md) | 게임 상태 HTTP 조회, 세션 로그인, CSRF 발급, 광고 선택 POST를 처리한다. 게임 상태 변경은 WebSocket 서비스가 소유한다. |
| `manage.py` | [문서](files/manage.py.md) | Django 관리 명령의 프로세스 진입점이다. 게임 규칙이나 Kafka 전송을 직접 구현하지 않고 Django 명령 탐색기에 argv를 넘긴다. |

### 게임 관리 명령

| 실제 파일 | 라우팅 문서 | 책임 |
|---|---|---|
| `game/management/commands/consume_game_sample.py` | [문서](files/game/management/commands/consume_game_sample.py.md) | 별도 분석 group으로 읽은 사실을 JSONL에 append하고 파일 내구성 확보 뒤 해당 record의 다음 offset을 commit한다. |
| `game/management/commands/create_player.py` | [문서](files/game/management/commands/create_player.py.md) | 새 인증 계정과 Player를 원자적으로 만들고 기존 Player 상태/비밀번호를 보존한다. |
| `game/management/commands/export_event_sample.py` | [문서](files/game/management/commands/export_event_sample.py.md) | 가장 최근 확정 GameEvent 한 건을 학습용 JSON 파일로 저장한다. |
| `game/management/commands/export_game_events.py` | [문서](files/game/management/commands/export_game_events.py.md) | 확정 MySQL GameEvent 전체를 Spark용 JSONL snapshot으로 내보낸다. |
| `game/management/commands/export_game_handoff.py` | [문서](files/game/management/commands/export_game_handoff.py.md) | 외부 분석 단계로 넘길 확정 GameEvent JSONL을 선택 시간 구간으로 내보낸다. |
| `game/management/commands/export_player_snapshot.py` | [문서](files/game/management/commands/export_player_snapshot.py.md) | Player 공개 상태를 player-snapshot/v1 NDJSON으로 내보내고 행 수·SHA-256을 출력한다. 임시 파일 완성 후 대상을 교체한다. |
| `game/management/commands/inspect_game_facts.py` | [문서](files/game/management/commands/inspect_game_facts.py.md) | 확정 MySQL 사실의 공개 식별자와 Outbox 발행 상태를 제한된 행 수로 조회한다. |
| `game/management/commands/inspect_game_offsets.py` | [문서](files/game/management/commands/inspect_game_offsets.py.md) | 레코드를 소비하거나 commit하지 않고 topic/group의 partition별 보존 시작·끝·저장 위치를 조회한다. |
| `game/management/commands/prepare_load_players.py` | [문서](files/game/management/commands/prepare_load_players.py.md) | 부하 테스트 계정 묶음을 만들고 공개 account manifest를 내보낸다. 기존 비밀번호를 덮어쓰지 않는다. |
| `game/management/commands/publish_game_events.py` | [문서](files/game/management/commands/publish_game_events.py.md) | MySQL Outbox의 미발행 확정 사실을 Kafka로 보내고 broker ack 후 published_at을 기록한다. |
| `game/management/commands/replay_game_events.py` | [문서](files/game/management/commands/replay_game_events.py.md) | settings.KAFKA_EVENT_TOPIC의 실행 시작 시 보존 구간을 고정해 독립 JSONL로 재읽는다. consumer group 위치를 바꾸지 않는다. |
| `game/management/commands/snapshot_game_actions.py` | [문서](files/game/management/commands/snapshot_game_actions.py.md) | 고정 game.actions.v1의 실행 시작 시 보존 구간을 고정해 독립 JSONL로 재읽는다. consumer group 위치를 바꾸지 않는다. |
| `game/management/commands/transform_game_actions.py` | [문서](files/game/management/commands/transform_game_actions.py.md) | 확정 사실 topic을 검증·필터·변환하여 별도의 행동 topic으로 발행하고 그 뒤 입력 offset을 commit한다. |
| `game/management/commands/watch_game_events.py` | [문서](files/game/management/commands/watch_game_events.py.md) | 관찰용 consumer group으로 확정 사실의 식별자와 Kafka 위치를 출력한다. Player/GameEvent DB를 바꾸지 않는다. |

### 분석 앱·관리 명령

| 실제 파일 | 라우팅 문서 | 책임 |
|---|---|---|
| `analytics/admin.py` | [문서](files/analytics/admin.py.md) | Django admin 모듈의 기본 자리다. 현재 모델 등록이나 관리 화면 구현은 없다. |
| `analytics/apps.py` | [문서](files/analytics/apps.py.md) | Django 앱 이름과 자동 기본키 형식을 등록한다. 수집·집계 작업을 시작하지 않는다. |
| `analytics/ingest_views.py` | [문서](files/analytics/ingest_views.py.md) | Kafka Parquet 수집 요약의 준비 여부·기본 계약을 검증해 조회한다. 수집 실행과 원문 evidence는 HTTP 응답에 포함시키지 않는다. |
| `analytics/management/commands/capture_ingest_environment.py` | [문서](files/analytics/management/commands/capture_ingest_environment.py.md) | 현재 설정된 수집 실행 환경을 관찰 파일로 남긴다. Spark를 실행했다는 증거를 생성하는 명령은 아니다. |
| `analytics/management/commands/collect_game_metrics.py` | [문서](files/analytics/management/commands/collect_game_metrics.py.md) | DB 확정 사실·발행 표식·Kafka 그룹 위치·마지막 Spark progress를 하나의 측정 snapshot으로 만든다. 레코드를 소비하거나 그룹 offset을 commit하지 않는다. |
| `analytics/management/commands/publish_window_demo.py` | [문서](files/analytics/management/commands/publish_window_demo.py.md) | 고정 event-time 단계의 합성 분석 레코드를 게임이 소비하지 않는 별도 demo topic에 발행한다. DB GameEvent나 실제 사용자 행동은 만들지 않는다. |
| `analytics/management/commands/run_game_delta.py` | [문서](files/analytics/management/commands/run_game_delta.py.md) | 기존 Spark 클러스터에 고유 game fact Delta 스트림을 제출한다. 명령 자체가 중복 제거를 구현하지 않는다. |
| `analytics/management/commands/run_game_ingest.py` | [문서](files/analytics/management/commands/run_game_ingest.py.md) | 독립 Kafka→Parquet 수집 작업을 기존 standalone Spark master에 제출한다. 게임 요약이나 Delta 원천과 다른 출력/checkpoint를 유지한다. |
| `analytics/management/commands/run_game_windows.py` | [문서](files/analytics/management/commands/run_game_windows.py.md) | Kafka 전달 레코드의 tumbling 또는 sliding 창 작업을 제출한다. 결과 파일 조회 요청과는 분리된 명령이다. |
| `analytics/management/commands/summarize_game.py` | [문서](files/analytics/management/commands/summarize_game.py.md) | raw DB 내보내기 또는 Delta 사실을 선택해 같은 화면용 game-summary 파일로 집계한다. |
| `analytics/management/commands/summarize_ingest.py` | [문서](files/analytics/management/commands/summarize_ingest.py.md) | 수집 Parquet 전용 요약과 선택 사건 evidence를 Spark에 맡긴다. game-summary.json을 변경하지 않는다. |
| `analytics/management/commands/summarize_windows.py` | [문서](files/analytics/management/commands/summarize_windows.py.md) | 확정된 Parquet 창에서 작은 조회용 windows.json을 게시하는 Spark 작업을 제출한다. |
| `analytics/models.py` | [문서](files/analytics/models.py.md) | analytics 앱의 모델 선언 자리다. 분석 결과는 이 파일의 ORM 모델이 아니라 DATA_DIR 아래 결과 파일을 통해 제공된다. |
| `analytics/urls.py` | [문서](files/analytics/urls.py.md) | config/urls.py의 api/analytics/ 하위에 세 조회 핸들러를 등록한다. 실행·쓰기 API는 등록하지 않는다. |
| `analytics/views.py` | [문서](files/analytics/views.py.md) | 게시된 게임 집계·bounded Kafka 스냅샷·시간 창·전달 측정·부하 측정 파일을 JSON으로 조회한다. 요청에서 Spark나 Kafka 작업을 시작하거나 게임 상태를 수정하지 않는다. |

### Spark 작업

| 실제 파일 | 라우팅 문서 | 책임 |
|---|---|---|
| `spark_jobs/add_game_date.py` | [문서](files/spark_jobs/add_game_date.py.md) | 고유 Silver 사건의 UTC 시각으로 서울 달력 날짜를 추가하고 날짜별 Parquet으로 저장한다. |
| `spark_jobs/bronze_preview.py` | [문서](files/spark_jobs/bronze_preview.py.md) | Kafka bounded snapshot JSON의 전달 위치와 분포를 살펴본다. 변환 결과 파일을 저장하지 않는다. |
| `spark_jobs/build_game_daily.py` | [문서](files/spark_jobs/build_game_daily.py.md) | 날짜가 붙은 Silver를 날짜·방·종류별 Gold 행동 수와 활동 플레이어 수로 집계한다. |
| `spark_jobs/check_game_quality.py` | [문서](files/spark_jobs/check_game_quality.py.md) | 펼친 Bronze를 정상 accepted와 사유별 quarantine으로 나눈다. 오류 자료를 정상 사건으로 보정하지 않는다. |
| `spark_jobs/dedup_game_actions.py` | [문서](files/spark_jobs/dedup_game_actions.py.md) | 정상 사건 전달에서 같은 event_id의 업무 내용 충돌을 거절하고 한 대표 전달을 선택한다. |
| `spark_jobs/game_actions_delta.py` | [문서](files/spark_jobs/game_actions_delta.py.md) | Kafka 전달 기록을 event_id별 첫 확정 사실 Delta 테이블에 병합한다. 원문 수집 Parquet과 별도 상태를 갖는다. |
| `spark_jobs/game_batch.py` | [문서](files/spark_jobs/game_batch.py.md) | raw 또는 Delta 입력의 game event_id 고유 건수를 화면용 game-summary.json으로 게시한다. |
| `spark_jobs/game_ingest.py` | [문서](files/spark_jobs/game_ingest.py.md) | Kafka game.actions 레코드의 전달 위치와 원문을 보존하며 valid/invalid/unsupported로 분류해 독립 Parquet에 append한다. 고유 사실 Delta를 만들거나 HTTP API를 제공하지 않는다. |
| `spark_jobs/game_windows.py` | [문서](files/spark_jobs/game_windows.py.md) | Kafka 전달 레코드를 event-time 창으로 센다. event_id별 고유 사실 집계가 아니라 중복 전달을 포함할 수 있는 창 건수다. |
| `spark_jobs/layout_benchmark.py` | [문서](files/spark_jobs/layout_benchmark.py.md) | Parquet 행수와 실제 파일수·총 bytes·평균 파일크기를 측정 보고서로 저장한다. |
| `spark_jobs/layout_codec.py` | [문서](files/spark_jobs/layout_codec.py.md) | 같은 Parquet 행을 Zstd와 Snappy로 저장·재읽기하며 실제 실행 시간을 측정한다. |
| `spark_jobs/layout_compact.py` | [문서](files/spark_jobs/layout_compact.py.md) | payload를 제외하고 열 순서를 맞춘 뒤 처리 partition을 줄여 Snappy Parquet을 쓰고 전후 행 차이를 검사한다. |
| `spark_jobs/layout_formats.py` | [문서](files/spark_jobs/layout_formats.py.md) | 같은 열 집합을 무압축 JSON과 Snappy Parquet으로 저장하고 재읽기 행수·스키마를 비교한다. |
| `spark_jobs/layout_partition.py` | [문서](files/spark_jobs/layout_partition.py.md) | 날짜 partition 저장 후 한 날짜 조건의 읽기 계획을 관찰한다. |
| `spark_jobs/layout_projection.py` | [문서](files/spark_jobs/layout_projection.py.md) | 필요한 열을 선택한 Parquet의 실행 계획·표본을 확인하고 새 출력에 저장한다. |
| `spark_jobs/layout_smallfiles.py` | [문서](files/spark_jobs/layout_smallfiles.py.md) | 처리 partition 수에 따른 실제 출력 파일수·행수·시간을 비교한다. |
| `spark_jobs/parse_game_bronze.py` | [문서](files/spark_jobs/parse_game_bronze.py.md) | Kafka 원본 snapshot의 value JSON을 업무 사건 필드로 펼쳐 Bronze Parquet에 저장한다. 품질 판정과 중복 제거는 후속 작업이다. |
| `spark_jobs/publish_game_summary.py` | [문서](files/spark_jobs/publish_game_summary.py.md) | 고유 Silver에서 작은 화면용 행동·방 집계를 만들어 지정 JSON 파일에 게시한다. |
| `spark_jobs/summarize_ingest.py` | [문서](files/spark_jobs/summarize_ingest.py.md) | 독립 수집 Parquet에서 전달 수·고유 valid 사건 수·중복 수를 계산하고 작은 HTTP 조회용 요약을 게시한다. 선택 event_id의 원문 evidence는 별도 파일로 남긴다. |
| `spark_jobs/summarize_windows.py` | [문서](files/spark_jobs/summarize_windows.py.md) | 확정 창 Parquet의 최신 일부 행만 조회용 JSON으로 게시한다. 진행 중 window state나 checkpoint를 조회 결과로 쓰지 않는다. |

### 검증·수집·인계·측정 도구

| 실제 파일 | 라우팅 문서 | 책임 |
|---|---|---|
| `tools/capture_game.py` | [문서](files/tools/capture_game.py.md) | Kafka `game.actions.v1`의 현재 파티션 범위를 고정해 원문 전달 기록을 NDJSON으로 수집한다. 게임 상태와 consumer group commit을 변경하지 않는다. |
| `tools/check_action_handoff.py` | [문서](files/tools/check_action_handoff.py.md) | 하나의 event_id에 대해 원본 사실과 표시 필드가 추가된 행동 snapshot을 비교한다. |
| `tools/check_bronze.py` | [문서](files/tools/check_bronze.py.md) | 사본 bytes를 원본 manifest의 bytes·sha256·rows와 비교한다. |
| `tools/check_encode_decode.py` | [문서](files/tools/check_encode_decode.py.md) | DB export의 첫 번째 비어 있지 않은 사실을 parser로 읽고 JSON UTF-8 왕복 결과를 비교한다. |
| `tools/check_game_event_jsonl.py` | [문서](files/tools/check_game_event_jsonl.py.md) | 고정 경로의 게임 사실 JSONL에서 첫 행의 필드 구성을 확인한다. |
| `tools/check_replay_file.py` | [문서](files/tools/check_replay_file.py.md) | snapshot JSONL의 전달 위치와 manifest의 고정 범위·행 수를 비교한다. |
| `tools/compare_compacted_summary.py` | [문서](files/tools/compare_compacted_summary.py.md) | 파일 정리 전후의 화면 집계를 비교한 뒤 compaction 정책을 기록한다. |
| `tools/compare_load.py` | [문서](files/tools/compare_load.py.md) | 저장된 두 WS 부하 결과를 나란히 읽고 요청 간격·요청 시간의 일치 여부를 출력한다. |
| `tools/copy_bronze.py` | [문서](files/tools/copy_bronze.py.md) | 같은 Bronze 실행의 이벤트와 manifest를 bytes 그대로 로컬 사본 폴더에 복사한다. |
| `tools/custom_error.py` | [문서](files/tools/custom_error.py.md) | 사본 경로의 실행 ID 오류를 표현하는 예외 타입을 정의한다. |
| `tools/export_transitions.py` | [문서](files/tools/export_transitions.py.md) | 서버 GameEvent export에서 수동 정책의 전이 행을 검증하고 별도 JSONL·manifest로 인계한다. 학습이나 세계 초기화는 수행하지 않는다. |
| `tools/find_nifi_event.py` | [문서](files/tools/find_nifi_event.py.md) | NiFi 출력 디렉터리의 제한된 파일 수에서 지정 event_id를 찾아 읽기 전용 증거를 출력한다. |
| `tools/inspect_action_snapshot.py` | [문서](files/tools/inspect_action_snapshot.py.md) | 행동 Topic snapshot의 범위·동일 사실 내용·표시 필드 추가 현황을 검사한다. |
| `tools/lake_inventory.py` | [문서](files/tools/lake_inventory.py.md) | 저장된 화면 집계와 분석 재생성 원천·게임 상태 소유 저장소를 계약 JSON으로 기록한다. |
| `tools/local_paths.py` | [문서](files/tools/local_paths.py.md) | Bronze 사본의 실행 ID·허용 파일명을 검증해 Path만 반환한다. 파일 I/O는 호출자가 한다. |
| `tools/read_group_samples.py` | [문서](files/tools/read_group_samples.py.md) | 두 consumer group 표본의 고유 event_id 수와 공통 사건 수를 읽는다. |
| `tools/read_load_result.py` | [문서](files/tools/read_load_result.py.md) | 저장된 WS 부하 결과의 주요 수치와 방별 연결 성공·명령 성공 수를 출력한다. |
| `tools/store_bronze.py` | [문서](files/tools/store_bronze.py.md) | 수집 NDJSON의 원본 bytes와 manifest를 새 Bronze 실행 폴더에 보존한다. |
| `tools/write_lake_contract.py` | [문서](files/tools/write_lake_contract.py.md) | 선택한 Bronze manifest의 버전·지문과 분석 재처리 정책을 계약 파일에 기록한다. |
| `tools/write_layer_contract.py` | [문서](files/tools/write_layer_contract.py.md) | Bronze·품질 결과·화면 summary로 Silver/Gold 계층 인계 계약을 작성한다. |
| `tools/ws_load.py` | [문서](files/tools/ws_load.py.md) | 각 계정별 Django 인증 세션과 WS 연결로 교실용 동시 이동 부하를 만들고 실제 응답 RTT·처리율을 저장한다. |

## 문서 갱신 규칙

1. 런타임 파일을 추가·이동·삭제하면 프로젝트 상대경로를 유지한 `files/<경로>.md`와 위 목차를 함께 갱신한다.
2. AST inventory로 실제 클래스·함수·직접 선언한 메서드를 먼저 추출한다. annotation·기본값·가변인자를 포함한 서명을 소스와 맞춘다.
3. 각 함수는 서명 → 검증/변환 → 직접 호출 → 반환/상태 변화 순서로 설명한다. 다른 파일의 내부 구현은 복제하지 않고 해당 문서로 연결한다.
4. URLconf·decorator가 바뀌면 등록 순서, 전체 경로, 허용 메서드, 인증·오류 계약을 함께 갱신한다. URL resolver는 HTTP 메서드로 다음 후보를 선택하지 않는다.
5. 원천·출력·checkpoint·게시 JSON·스키마가 바뀌면 분석 흐름 문서와 해당 관리 명령/Spark 파일 문서를 함께 갱신한다.
6. 파일 대응·정확한 서명·내부 링크·호출 의미를 검사한다. 정적 문서 검사가 실제 DB/Kafka/Spark/HTTP 실행 성공을 증명하지는 않는다.
