# `game/management/commands/inspect_game_offsets.py`

## 책임과 경계

레코드를 소비하거나 commit하지 않고 topic/group의 partition별 보존 시작·끝·저장 위치를 조회한다.

## 값과 데이터 계약

`--topic` game.events.v1, `--group` day13-analysis-a.

## 연결

[game/management/commands/consume_game_sample.py](consume_game_sample.py.md) · [game/management/commands/replay_game_events.py](replay_game_events.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 8.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 11.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--topic` game.events.v1, `--group` day13-analysis-a.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 15.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** partitions_for_topic 결과가 None이면 CommandError. partition 번호를 정렬해서 TopicPartition으로 바꾼다. poll/seek/commit은 호출하지 않는다.
- **직접 호출:** `KafkaConsumer(enable_auto_commit=False,request_timeout_ms=15000)` → `partitions_for_topic` → `beginning_offsets/end_offsets` → partition별 `committed`.
- **반환·상태:** beginning_offset/end_offset/committed_offset/has_committed_offset JSON을 출력한다. finally에서 close(autocommit=False)와 stdout 출력이 실행되므로 metadata 오류 때도 빈/부분 rows 출력 뒤 오류가 전파될 수 있다. end/committed는 다음 읽을 위치이며 None은 미commit이다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
