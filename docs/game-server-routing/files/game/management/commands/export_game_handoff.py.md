# `game/management/commands/export_game_handoff.py`

## 책임과 경계

외부 분석 단계로 넘길 확정 GameEvent JSONL을 선택 시간 구간으로 내보낸다.

## 값과 데이터 계약

`--output` 필수, `--since`/`--until` 선택 ISO timestamp.

## 연결

[game/models.py](../../models.py.md) · [game/services.py](../../services.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 10.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 13.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--output` 필수, `--since`/`--until` 선택 ISO timestamp.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 18.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** Z를 +00:00으로 바꾸어 datetime으로 읽고 timezone 없는 입력을 CommandError로 거부한다. since는 >=, until은 <이며 since<=until을 따로 검사하지 않는다.
- **직접 호출:** `GameEvent.objects.order_by` → `datetime.fromisoformat` → 조건부 query.filter → `Path.resolve/mkdir/open` → `query.iterator(chunk_size=1000)` → `event_time.astimezone(UTC).isoformat` → `stream.write` → `temporary.replace`.
- **반환·상태:** schema_version1 envelope의 event_time을 UTC ISO 문자열로 내보낸다. 임시파일 suffix는 원래 suffix+".tmp"이며 성공 시 output 교체. count/output 출력; DB와 발행 상태를 변경하지 않는다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
