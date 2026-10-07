# `game/management/commands/export_game_events.py`

## 책임과 경계

확정 MySQL GameEvent 전체를 Spark용 JSONL snapshot으로 내보낸다.

## 값과 데이터 계약

사용자 정의 옵션은 없다. 출력 위치는 settings.DATA_DIR/raw/game-events.jsonl이다.

## 연결

[game/models.py](../../models.py.md) · [game/services.py](../../services.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 7.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 9.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** 필터 없이 event_time/event_id 순으로 읽으며 빈 테이블도0줄 파일로 성공한다.
- **직접 호출:** `target.parent.mkdir` → `target.with_suffix` → `GameEvent.objects.order_by` → `iterator(chunk_size=500)` → `serialize_event/json.dumps/stream.write` → `temporary.replace(target)`.
- **반환·상태:** game-events.jsonl.tmp에 전체 결과를 쓴 뒤 최종 파일을 교체한다. count/path 출력, DB/published_at 변경 없음. 한 DB snapshot transaction을 잡는 코드는 없다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
