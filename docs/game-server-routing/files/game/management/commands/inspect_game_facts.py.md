# `game/management/commands/inspect_game_facts.py`

## 책임과 경계

확정 MySQL 사실의 공개 식별자와 Outbox 발행 상태를 제한된 행 수로 조회한다.

## 값과 데이터 계약

`--rows` int choices3/5/10, 기본5.

## 연결

[game/models.py](../../models.py.md) · [game/management/commands/publish_game_events.py](publish_game_events.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 5.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 8.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--rows` int choices3/5/10, 기본5.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 11.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** parser choices로 행 수를 제한한다. 최신순(event_time,event_id 내림차순)으로 선택하며 payload 전체를 출력하지 않는다.
- **직접 호출:** `GameEvent.objects.order_by(...)[...rows]` → event별 `payload.get/keys`, 시간 `isoformat` → `GameEvent.objects.count/filter(...).count` → `stdout.write`.
- **반환·상태:** event_id/command_id/player_id/event_type/room_id/event_time/published_at/payload_keys/has_transition 행과 delivery_summary를 출력한다. DB를 바꾸지 않는다. 최신 행 수와 합계 조회는 별도 query다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
