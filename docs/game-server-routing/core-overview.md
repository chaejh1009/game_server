# game_server CORE 호출 지도

[전체 라우팅 목차](README.md)

이 문서는 2026-10-08 현재 `manage.py`, `config/*.py`, `game/*.py`, `game/management/commands/*.py`의 실제 소스를 기준으로 작성했다. top-level 함수·클래스·메서드는 스킬의 AST inventory로 추출했다. 교안 overlay나 계획된 기능을 현재 구현으로 간주하지 않았다. 원본 Python 파일과 .env는 변경하지 않았고 .env는 읽지 않았다.

## 진입점과 소유 경계

| 진입점 | 다음 경계 | 소유하는 일 |
| --- | --- | --- |
| [manage.py](files/manage.py.md) | Django execute_from_command_line → 선택 Command | 관리 명령 실행 |
| [config/asgi.py](files/config/asgi.py.md) HTTP | Django ASGI → [config/urls.py](files/config/urls.py.md) | HTTP route·middleware |
| config/asgi.py WebSocket | AllowedHostsOriginValidator → AuthMiddlewareStack → URLRouter | origin·session 인증·WS route |
| [config/wsgi.py](files/config/wsgi.py.md) | Django WSGI → config.urls | HTTP 전용 진입점 |
| [game/routing.py](files/game/routing.py.md) | [PlayConsumer](files/game/consumers.py.md) | /ws/play/ 연결과 방 broadcast |
| [game/services.py](files/game/services.py.md) | [Player·GameEvent](files/game/models.py.md) | 규칙·멱등 처리·원자적 상태/사실 저장 |
| [game/ad_gateway.py](files/game/ad_gateway.py.md) | 광고 서버 HTTP | Player→subject, 매체 header·응답 검증 |

## 실제 HTTP route

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

## WebSocket route와 메시지

`/ws/play/` → [PlayConsumer.as_asgi()](files/game/consumers.py.md). 인증되지 않으면4401, 같은 player_id가 현재 프로세스 ONLINE에 있으면4409로 닫는다. 로그인했지만 Player가 없을 때의 read_player 예외를 connect가 별도로 잡지 않는다.

```text
config.asgi.application[websocket]
  AllowedHostsOriginValidator
    AuthMiddlewareStack
      URLRouter(game.routing.websocket_urlpatterns)
        PlayConsumer.connect
          read_player -> Player.get -> serialize_player
          ONLINE 등록 -> group_add -> accept -> state 전송
          group_send(type="room.snapshot")
            room_snapshot -> read_room -> snapshot 전송

PlayConsumer.receive_json(command)
  dict 검사 -> 0.2초 간격 검사
  run_command(database_sync_to_async(apply_command))
    UUID 정규화 -> Player 행 잠금 -> command_id 중복 확인
    규칙 검사 -> Player 저장 + GameEvent 생성 (하나의 transaction)
  group_send(type="room.state",state=...)
    room_state -> state 전송

PlayConsumer.disconnect
  자신의 ONLINE 연결만 삭제 -> group_discard -> room.snapshot 요청
```

클라이언트 명령은 `{command_id: UUID문자열, type: move|gather|train}`이며 move에 direction=up/down/left/right를 추가한다. 초기/변경 state는 `{player_id,type:"state",room_id,x,y,coins,version}`이고 명령 결과에는 command_id가 붙는다. snapshot은 `{type:"snapshot",players:[state,...]}`, 실패는 `{type:"error",code,command_id}`다. `ONLINE`과 InMemoryChannelLayer는 프로세스 내부 상태이므로 여러 서버 프로세스의 접속·broadcast를 통합하지 않는다.

## 게임 상태와 확정 사실의 계약

맵은 20×15, 채집 (2,2), 수련 (3,2)이다. 성공 명령은 version을 증가시키고 같은 transaction에 GameEvent를 만든다. 같은 Player의 같은 command_id를 다시 받으면 새 변경/이벤트 없이 현재 state를 반환한다. command_id는 payload 조회로 중복을 찾으며 별도 unique column은 없다.

```text
apply_command
  before observe_player
  next_transition_position -> 이전 미완료 episode step+1 또는 새 episode step1
  move/gather/train -> after observe_player
  transition = observation/action/reward/next_observation
               episode_id/step/done/terminated/truncated/policy_version
  GameEvent(payload.command_id + state + transition)

publish_game_events
  GameEvent(published_at IS NULL)
    serialize_event -> Kafka send(key=player_id) -> broker ack
      published_at 기록
```

transition은5번째 step에서 done/truncated=True, terminated=False이며 reward는 coins의 증가량, policy_version은 manual-v1이다. 사실 envelope은 `{schema_version:1,event_id,event_type,player_id,room_id,event_time,payload}`다. UUID event_id는 문자열, player_id는 정수, event_time은 timezone을 포함한 ISO 문자열이다. published_at은 Kafka 발행 진행 상태이며 envelope에는 포함하지 않는다. ack 후 DB 기록 전 장애는 재전송을 만들 수 있어 downstream은 event_id로 중복을 다뤄야 한다.

## 광고 선택·이벤트 호출

```text
POST /api/ads/decision/ {slot_id}
  views.ad_decision
    session user -> Player
    slot whitelist(village-board,lobby-banner)
    request_decision(player,slot_id)
      POST ad_server /api/media/decision/
      headers: X-Media-ID + X-Media-Key
      body: media_id + subject{media_id,subject_id=str(Player.pk)}
            + slot_id + context{}
      empty/ad=null 정규화 또는 slot_id 검사

POST /api/ads/events/ {decision_id,event_type}
  ad_events.ad_event
    session user -> Player
    dict와 정확히 두 입력 key 검사 (추가·누락 key 거부)
    request_ad_event(player,decision_id,event_type)
      call_ads -> POST ad_server /api/media/events/
      headers: X-Media-ID + X-Media-Key
      body: media_id + Player에서 만든 subject + decision_id + event_type
      event_id==decision_id+":"+event_type, event_type, bool created 검사
    {event_id,event_type,created} + Cache-Control:no-store
```

`game:ad-events`는 `/api/ads/events/`로 reverse된다. CSRF middleware가 요청을 먼저 거부하면403이며, 뷰에 도달한 요청은 POST 제한405 → 미인증401 → Player 없음409 → JSON/입력 검사 순으로 처리한다. JSON 파싱 실패, 잘못된 키 집합, gateway의 로컬 입력 검증 실패는400 `ad_event_rejected`다. gateway는 decision_id가 비어 있지 않은128자 이하 문자열인지 검사하며 UUID 형식 자체는 검사하지 않는다.

subject는 조회 번호나 문자열 하나가 아니라 `{media_id,subject_id}` 객체다. 클라이언트는 subject/campaign_id를 이벤트 API에 넘기지 않는다. 선택된 **decision_id**와 impression/click만 보낸다. Player PK, campaign ID, bid 문서 ID는 decision ID의 대체값이 아니다. 실제 표시 여부와 클릭 순서의 판단은 클라이언트와 광고 서버가 맡으며 게임 bridge는 표시를 추정하거나 임의 impression을 만들지 않는다.

선택 응답은 기존 광고/이미지 필드를 보존하면서 body/bid_amount 기본 필드를 보완한다. 이벤트200의 created=False도 중복 접수에 대한 정상 응답이다. 이벤트400의 안전한 code는 decision_snapshot_missing, decision_not_found_for_subject, impression_required, decision_id_required, event_type_invalid이며 그 밖의 거절은 ad_event_rejected다. upstream503·통신/검증 실패는503으로 나타낸다. 서버 간 비200 중503 이외는 ValueError를 통해 게임 bridge의400으로 매핑한다. 광고 서버의 임의 원문 오류를 그대로 보내지 않는다.

## 게임 관리 명령의 역할

모두 game_server 루트에서 `python manage.py <명령명> ...`으로 Django가 찾는 Command다. 실행 예시는 설정·DB·Kafka 등의 부작용이 있으므로 이 문서 작성 과정에서는 실행하지 않았다.

| 명령 | 읽는 곳 → 쓰는 곳 | 재실행/상태 계약 |
| --- | --- | --- |
| [create_player](files/game/management/commands/create_player.py.md) | 사용자 입력 → User·Player | 기존 상태/비밀번호 보존, 새 방 정원20 |
| [prepare_load_players](files/game/management/commands/prepare_load_players.py.md) | 사용자 입력 → User·Player·accounts JSON | 기존 비밀번호/방 불일치 거부,20명 단위 방 |
| [inspect_game_facts](files/game/management/commands/inspect_game_facts.py.md) | MySQL → stdout | 공개 최신3/5/10행과 Outbox 합계, 읽기 전용 |
| [export_event_sample](files/game/management/commands/export_event_sample.py.md) | MySQL 최신1행 → sample JSON | samples/game-event.json 직접 덮어쓰기 |
| [export_game_events](files/game/management/commands/export_game_events.py.md) | MySQL 전체 → raw JSONL | 임시파일 완성 후 교체; published_at 변경 없음 |
| [export_game_handoff](files/game/management/commands/export_game_handoff.py.md) | MySQL [since,until) → 지정 JSONL | timezone 필수, UTC event_time, 임시파일 교체 |
| [export_player_snapshot](files/game/management/commands/export_player_snapshot.py.md) | Player 공개 상태 → 지정 NDJSON·stdout 메타데이터 | 시간대 검사, 임시 파일 교체, 행 수·SHA-256; DB 변경 없음 |
| [publish_game_events](files/game/management/commands/publish_game_events.py.md) | 미발행 Outbox → Kafka·published_at | ack 뒤 발행 시각; 재전송 가능 |
| [watch_game_events](files/game/management/commands/watch_game_events.py.md) | Kafka → stdout·group offset | 관찰 group에서 처리 batch 뒤 수동 commit |
| [consume_game_sample](files/game/management/commands/consume_game_sample.py.md) | Kafka → append JSONL·group offset | write/flush/fsync 뒤 offset+1 commit |
| [inspect_game_offsets](files/game/management/commands/inspect_game_offsets.py.md) | Kafka metadata → stdout | poll/commit 없음; 읽기 전용 |
| [replay_game_events](files/game/management/commands/replay_game_events.py.md) | 사실 topic 보존 구간 → 독립 JSONL/manifest | group 없음·commit 없음·기존 결과 거부 |
| [transform_game_actions](files/game/management/commands/transform_game_actions.py.md) | 사실 topic → 행동 topic·group offset | 검증/필터/변환; ack 또는 필터 뒤 commit |
| [snapshot_game_actions](files/game/management/commands/snapshot_game_actions.py.md) | game.actions.v1 보존 구간 → 독립 JSONL/manifest | 출력 파일명은 실제 코드상 game-events.jsonl |

사실→행동 변환 함수는 [game/transforms.py](files/game/transforms.py.md)에 있다. parse_game_event는 bytes/필수필드/schema/UUID/정수 player/timezone을 검사한다. is_game_action은 세 event_type만 고르고, with_action_label은 deepcopy한 payload에 한국어 이름을 붙여 원본 event_id/key/player_id를 유지한다.

### Player 공개 상태 내보내기 호출 흐름

```text
manage.py export_player_snapshot --output <경로>
  -> Command.add_arguments: 필수 출력 경로 등록
  -> Command.handle: 부모 디렉터리 생성·공통 captured_at 확보
    -> Player.objects.order_by("id").values(...).iterator()
    -> updated_at 시간대 검사·NDJSON 임시 파일 작성
    -> 완성 파일 SHA-256 계산 -> os.replace로 대상 교체
    -> stdout에 경로·행 수·체크섬·스키마·수집 시각 JSON 출력
```

기존 대상은 성공 시 교체하며 별도 manifest를 만들지 않는다. Player가 없으면 빈 파일을 게시하고 stdout의 captured_at은 null이다. 조회 전체를 고정하는 별도 transaction이 없어 captured_at이 DB 전체의 일관된 시점을 보장하지 않는다. 출력 필드와 예외 처리 범위는 [파일별 문서](files/game/management/commands/export_player_snapshot.py.md), 실행 예시는 [프로젝트 README](../../README.md#플레이어-공개-상태-내보내기)를 따른다.

## 파일별 상세 문서

| 영역 | 문서 |
| --- | --- |
| 관리 진입 | [manage.py](files/manage.py.md) |
| 설정·HTTP·ASGI·WSGI | [config/settings.py](files/config/settings.py.md), [config/urls.py](files/config/urls.py.md), [config/asgi.py](files/config/asgi.py.md), [config/wsgi.py](files/config/wsgi.py.md) |
| 게임 모델·서비스 | [game/models.py](files/game/models.py.md), [game/services.py](files/game/services.py.md), [game/transforms.py](files/game/transforms.py.md) |
| HTTP·WS | [game/urls.py](files/game/urls.py.md), [game/views.py](files/game/views.py.md), [game/routing.py](files/game/routing.py.md), [game/consumers.py](files/game/consumers.py.md) |
| 광고 bridge | [game/ad_gateway.py](files/game/ad_gateway.py.md), [game/ad_events.py](files/game/ad_events.py.md) |
| 앱 등록 | [game/apps.py](files/game/apps.py.md), [game/admin.py](files/game/admin.py.md) |
| 관리 명령 | 위14개 명령 문서 |

## 범위와 제외 목록

CORE 문서는30개 Python 파일·78개 AST 기호를 포함한다. 설정/URL/admin처럼 기호가0개인 파일도 모듈 등록 값과 순서를 문서화했다. 함수 안의 decorator closure는 top-level inventory에 포함하지 않지만 viewer_methods의 실행 흐름에서 설명했다.

제외한 테스트: `game/tests.py`, `game/test_ad_gateway.py`, `game/test_transforms.py`. 제외한 migration: `game/migrations/0001_initial.py`, `game/migrations/__init__.py` 및 migrations 하위 전체. 제외한 빈 패키지 파일: `config/__init__.py`, `game/__init__.py`. analytics·spark·tools는 [전체 라우팅 목차](README.md)와 [분석 흐름 문서](analytics-overview.md)에 연결되어 있다. template/static/설정 환경값/DB 실제 데이터와 실행 중 서버 상태는 이 Python routing inventory의 대상이 아니다.

문서 검증은 AST 기호·정확한 signature·프로젝트 상대 파일 링크·core-inventory.json을 대조하는 정적 검사다. DB/Kafka/광고 서버의 실제 연결 성공이나 브라우저 렌더링 테스트를 수행했다는 뜻은 아니다.
