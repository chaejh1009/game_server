# `game/management/commands/transform_game_actions.py`

## 책임과 경계

확정 사실 topic을 검증·필터·변환하여 별도의 행동 topic으로 발행하고 그 뒤 입력 offset을 commit한다.

## 값과 데이터 계약

`--group` village-actions-v1, `--output-topic` game.actions.v1, `--max-events` int0(계속 실행).

## 연결

[game/transforms.py](../../transforms.py.md) · [game/management/commands/snapshot_game_actions.py](snapshot_game_actions.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 9.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 12.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--group` village-actions-v1, `--output-topic` game.actions.v1, `--max-events` int0(계속 실행).
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 17.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** 입출력 topic 같음, max-events 음수, 정본과 다른 group은 CommandError. 매 record의 envelope과 key==str(player_id).encode를 검사한다. 비행동은 출력 없이 filtered 처리한다.
- **직접 호출:** `KafkaConsumer/KafkaProducer` → `poll(max_records=1)` → `parse_game_event` → `is_game_action` → 행동일 때 `with_action_label/producer.send(...).get(10)` → `consumer.commit(OffsetAndMetadata(offset+1,"",-1))`.
- **반환·상태:** 성공 발행 ack 또는 정상 필터 판단 후 입력 offset을 commit한다. event_id/player_id/key를 보존한다. 입력/출력 위치와 read/emitted/filtered 합계를 출력한다. ack 후 commit 전 장애로 출력 중복은 가능하다. KeyboardInterrupt 처리; finally flush→close producer→close consumer(autocommit=False), DB 변경 없음.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
