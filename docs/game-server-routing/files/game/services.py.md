# `game/services.py`

## 책임과 경계

게임 규칙, 명령 멱등 처리, 전이 데이터, Player와 GameEvent의 원자적 저장을 소유한다. 네트워크 전송과 광고 선택은 하지 않는다.

## 값과 데이터 계약

`DIRECTIONS`: up/down/left/right의 좌표 증분. 맵은 WIDTH=20, HEIGHT=15, 채집은 (2,2), 수련은 (3,2)이다. EPISODE_STEPS=5이며 수동 정책 버전은 manual-v1이다.

상태 JSON은 player_id/type=state/room_id/x/y/coins/version, 이벤트 envelope은 schema_version/event_id/event_type/player_id/room_id/event_time/payload다. apply_command 반환에는 command_id가 추가된다.

## 연결

[game/models.py](models.py.md) · [game/consumers.py](consumers.py.md) · [game/management/commands/publish_game_events.py](management/commands/publish_game_events.py.md)

## 함수·클래스 목록

## `def observe_player(player)`

소스 기호: `observe_player` · 정의 줄: 13.

- **입력·역할:** player ORM 인스턴스를 받는다.
- **검사·변환:** x/y/coins만 새 dict로 선택한다.
- **직접 호출:** 외부 함수 호출은 없다.
- **반환·상태:** 관찰 dict를 반환한다. 원본 player를 바꾸지 않는다.

## `def next_transition_position(player)`

소스 기호: `next_transition_position` · 정의 줄: 20.

- **입력·역할:** player의 가장 최근 확정 GameEvent를 기준으로 다음 episode 위치를 계산한다.
- **검사·변환:** event_time/event_id 내림차순 첫 행의 payload.transition을 읽는다. 이전 transition이 있고 done이 거짓이면 같은 episode의 step+1, 없거나 종료됐으면 새 episode의 1이다.
- **직접 호출:** `GameEvent.objects.filter(...).order_by(...).first()` → 필요 시 `int(previous["step"])` 또는 `str(uuid4())`.
- **반환·상태:** `(episode_id, step)` tuple을 반환한다. malformed transition을 복구하는 별도 guard는 없다.

## `def serialize_player(player)`

소스 기호: `serialize_player` · 정의 줄: 32.

- **입력·역할:** player ORM 인스턴스를 받는다.
- **검사·변환:** 공개 상태 필드만 선택한다. player_id는 정수 PK다.
- **직접 호출:** 외부 함수 호출은 없다.
- **반환·상태:** type=state dict를 반환한다. user/비밀번호/광고 키는 포함하지 않는다.

## `def serialize_event(event)`

소스 기호: `serialize_event` · 정의 줄: 43.

- **입력·역할:** event ORM 인스턴스를 받는다.
- **검사·변환:** UUID를 문자열, event_time을 ISO 문자열로 바꾼다. payload는 그대로 참조한다.
- **직접 호출:** `str(event.event_id)` → `event.event_time.isoformat()`.
- **반환·상태:** schema_version=1 envelope을 반환한다. published_at은 envelope에 넣지 않는다.

## `def apply_command(user_id, command)`

소스 기호: `apply_command` · 정의 줄: 56.

- **입력·역할:** 인증된 user_id와 command dict(command_id UUID, type, move의 direction)를 받는다. consumer가 네트워크 사용자와 연결한다.
- **검사·변환:** UUID를 정규화하고 Player를 select_for_update로 잠근다. 같은 player+payload.command_id가 이미 있으면 현재 상태만 반환한다. move는 방향/맵 경계, gather/train은 지정 타일을 검사하며 나머지는 ValueError다.
- **직접 호출:** `UUID` → `Player.objects.select_for_update().get` → `GameEvent.objects.filter(...).first` → `observe_player` → `next_transition_position` → `player.save` → `observe_player` → `GameEvent.objects.create` → `serialize_player`.
- **반환·상태:** @transaction.atomic 안에서 player.version을 1 늘리고 상태와 확정 사실을 함께 저장한다. 5번째 step은 done/truncated=True, terminated=False이며 reward는 coins 차이다. 반환은 command_id를 포함한 state다. 예외면 transaction이 rollback된다. 중복 명령은 새 이벤트·version 증가 없이 현재 state를 반환한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
