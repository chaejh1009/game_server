# `game/consumers.py`

## 책임과 경계

인증 세션 WebSocket의 연결·방 broadcast·수신 빈도 제한을 소유한다. 동기 ORM/게임 서비스 호출은 database_sync_to_async로 감싸 비동기 소비자와 분리한다.

## 값과 데이터 계약

`run_command = database_sync_to_async(apply_command)`는 동기 게임 서비스를 await 가능한 호출로 감싼다. `ONLINE`은 player_id → channel_name dict이며 현재 프로세스 메모리만 공유한다. 방 group은 `room.<room_id>`, 입력 간격 하한은 0.2초다.

메시지는 초기 state, snapshot(players), 변경 state 또는 error(code,command_id)다. room.snapshot/room.state는 Channels 이벤트 이름이며 room_snapshot/room_state 메서드로 전달된다.

## 연결

[config/asgi.py](../config/asgi.py.md) · [game/routing.py](routing.py.md) · [game/models.py](models.py.md) · [game/services.py](services.py.md)

## 함수·클래스 목록

## `def read_player(user_id)`

소스 기호: `read_player` · 정의 줄: 8.

- **입력·역할:** 인증 user_id를 받는 동기 ORM 함수이며 @database_sync_to_async로 감싸져 있다.
- **검사·변환:** Player.objects.get이므로 미등록 Player는 DoesNotExist를 올린다.
- **직접 호출:** `Player.objects.get(user_id=user_id)` → `serialize_player`.
- **반환·상태:** await 결과로 공개 state dict를 전달한다.

## `def read_room(room_id, player_ids)`

소스 기호: `read_room` · 정의 줄: 16.

- **입력·역할:** room_id와 현재 ONLINE의 player_id 목록을 받는다.
- **검사·변환:** 같은 방이면서 pk__in에 있는 Player만 id 순서로 선택한다.
- **직접 호출:** `Player.objects.filter(...).order_by("id")` → 각 `serialize_player`.
- **반환·상태:** await 결과로 state dict 목록을 반환한다. 접속 정보의 source는 프로세스의 ONLINE이다.

## `PlayConsumer` · `class PlayConsumer(AsyncJsonWebsocketConsumer)`

소스 기호: `PlayConsumer` · 정의 줄: 20.

- **입력·역할:** Channels가 연결별 인스턴스를 생성하는 AsyncJsonWebsocketConsumer다.
- **검사·변환:** connect/disconnect가 group·ONLINE 수명을 관리한다. 인스턴스 속성은 연결마다 분리되고 ONLINE은 모듈 공유다.
- **직접 호출:** 각 lifecycle/event 메서드가 하위 Channels API와 게임 서비스를 호출한다.
- **반환·상태:** 게임 state는 DB가 소유하고 consumer는 전송용 state를 보관/중계한다.

## `async def connect(self)`

소스 기호: `PlayConsumer.connect` · 정의 줄: 21.

- **입력·역할:** scope["user"]와 channel_name을 사용한다.
- **검사·변환:** 인증 실패 close4401. read_player 후 이미 ONLINE에 같은 player_id가 있으면 close4409. Player 없음 예외를 자체 처리하지 않는다.
- **직접 호출:** `read_player` → `channel_layer.group_add` → `accept` → `send_json(state)` → `group_send(room.snapshot)`.
- **반환·상태:** self.player_id/room_id/group/last_action과 ONLINE을 설정한다. 반환은 None; 초기 상태와 방 snapshot을 전송한다.

## `async def room_snapshot(self, event)`

소스 기호: `PlayConsumer.room_snapshot` · 정의 줄: 43.

- **입력·역할:** Channels의 room.snapshot event를 받는다. event body는 사용하지 않는다.
- **검사·변환:** 현재 room_id와 ONLINE 키 목록으로 같은 방 플레이어를 다시 조회한다.
- **직접 호출:** `read_room` → `send_json`.
- **반환·상태:** {type:snapshot,players:[...]}를 연결에 보낸다. Player 상태는 바꾸지 않는다.

## `async def room_state(self, event)`

소스 기호: `PlayConsumer.room_state` · 정의 줄: 47.

- **입력·역할:** event["state"]를 받는다.
- **검사·변환:** 내용을 추가 변환하지 않는다.
- **직접 호출:** `send_json(event["state"])`.
- **반환·상태:** 방 broadcast된 state를 자신의 연결에 전송한다.

## `async def receive_json(self, content, **kwargs)`

소스 기호: `PlayConsumer.receive_json` · 정의 줄: 50.

- **입력·역할:** content와 추가 keyword args를 받는다. command_id는 dict일 때만 추출한다.
- **검사·변환:** 객체가 아니면 object_required, 0.2초 이내면 too_fast를 보내고 끝낸다. 통과 즉시 last_action을 갱신하므로 실패한 게임 명령도 빈도 제한에 포함된다.
- **직접 호출:** `time.monotonic` → `run_command(self.user.pk, content)` → 성공 시 `group_send(room.state)`; ValueError/KeyError/TypeError/AttributeError는 `send_json(error)`.
- **반환·상태:** 성공 state를 같은 방으로 broadcast한다. 실패의 code는 str(exc)이며 command_id를 되돌린다. DB 변경은 apply_command의 transaction 책임이다.

## `async def disconnect(self, close_code)`

소스 기호: `PlayConsumer.disconnect` · 정의 줄: 69.

- **입력·역할:** 연결 종료 code를 받는다. 일부만 초기화된 self도 허용한다.
- **검사·변환:** ONLINE 값이 자신의 channel_name일 때만 제거한다. group이 있으면 나간다.
- **직접 호출:** `getattr` → `ONLINE.get/pop` → `group_discard` → `group_send(room.snapshot)`.
- **반환·상태:** 프로세스 접속 추적에서 연결을 정리하고 남은 방 구성원에게 snapshot 갱신을 요청한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
