# `game/transforms.py`

## 책임과 경계

Kafka 사실 envelope을 검증하고 허용 게임 행동에 한국어 표시 이름을 붙이는 순수 변환 모듈이다. consumer group·offset·전송은 소유하지 않는다.

## 값과 데이터 계약

`REQUIRED_FIELDS`는 schema_version/event_id/event_type/player_id/room_id/event_time/payload. ACTION_LABELS는 player.moved→이동, player.gathered→개인 채집, player.trained→개인 수련이다.

## 연결

[game/services.py](services.py.md) · [game/management/commands/transform_game_actions.py](management/commands/transform_game_actions.py.md)

## 함수·클래스 목록

## `def parse_game_event(raw_value)`

소스 기호: `parse_game_event` · 정의 줄: 22.

- **입력·역할:** Kafka value의 bytes를 받는다.
- **검사·변환:** null 거부 → UTF8/JSON decode → dict/필수 필드/schema1/UUID 검사 → player_id 정확한 int(bool 거부), event_type/room_id 문자열, payload dict 검사 → offset 있는 ISO time 검사.
- **직접 호출:** `json.loads(raw_value.decode("utf-8"))` → `UUID` → `datetime.fromisoformat(event_time.replace("Z","+00:00"))`.
- **반환·상태:** 원본 event dict를 반환한다. 시간 필드를 datetime으로 교체하지 않으며 decode/검증 오류는 호출자에게 올린다.

## `def is_game_action(event)`

소스 기호: `is_game_action` · 정의 줄: 49.

- **입력·역할:** 검증된 event dict를 받는다.
- **검사·변환:** event_type이 ACTION_LABELS key에 있는지만 검사한다.
- **직접 호출:** 외부 함수 호출은 없다.
- **반환·상태:** bool을 반환한다. 모든 envelope 필드를 다시 검사하지 않는다.

## `def with_action_label(event)`

소스 기호: `with_action_label` · 정의 줄: 52.

- **입력·역할:** 검증된 게임 행동 event를 받는다.
- **검사·변환:** is_game_action이 거짓이면 ValueError. deepcopy 후 payload.action_label만 추가/교체한다.
- **직접 호출:** `is_game_action` → `deepcopy`.
- **반환·상태:** 원본을 변경하지 않은 dict를 반환하며 event_id/player_id와 기존 payload를 보존한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
