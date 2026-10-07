# `game/management/commands/replay_game_events.py`

## 책임과 경계

settings.KAFKA_EVENT_TOPIC의 실행 시작 시 보존 구간을 고정해 독립 JSONL로 재읽는다. consumer group 위치를 바꾸지 않는다.

## 값과 데이터 계약

`--output` 필수, `--max-records` int100000, `--timeout-seconds` int120.

## 연결

[game/management/commands/inspect_game_offsets.py](inspect_game_offsets.py.md) · [game/management/commands/transform_game_actions.py](transform_game_actions.py.md)

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
- **검사·변환:** `--output` 필수, `--max-records` int100000, `--timeout-seconds` int120.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 18.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** max-records1..1000000, timeout5..600, output 파일명 game-events.jsonl 및 경로 요소 data-replay를 검사한다. output/.partial/.manifest.json 중 기존 파일이 있으면 거부한다. topic/partition 없음, 시간/레코드 상한 초과는 CommandError다.
- **직접 호출:** `Path.resolve/exists/mkdir` → `KafkaConsumer(group_id=None,enable_auto_commit=False)` → `partitions_for_topic/assign/beginning_offsets/end_offsets/seek` → `pause/poll/position` → `destination.write` → `temporary.replace` → `manifest_path.write_text`.
- **반환·상태:** 시작의 [beginning,end)만 읽고 끝난 partition은 pause한다. Kafka 위치를 추가한 envelope을 .jsonl.partial에 exclusive 생성하며 모든 partition 완료 뒤 최종 JSONL로 교체한다. bounds와 group_committed:false manifest를 저장·출력한다. 실패 partial은 남기며 성공 입력으로 쓰지 않는다. manifest 저장은 final replace 이후이므로 두 파일을 한 transaction으로 묶지 않는다. finally close(autocommit=False); commit 호출은 없다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
