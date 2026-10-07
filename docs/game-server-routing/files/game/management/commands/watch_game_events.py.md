# `game/management/commands/watch_game_events.py`

## 책임과 경계

관찰용 consumer group으로 확정 사실의 식별자와 Kafka 위치를 출력한다. Player/GameEvent DB를 바꾸지 않는다.

## 값과 데이터 계약

`--group` 기본 village-watch-v1, `--limit` int 기본10. 별도 양수 guard는 없다.

## 연결

[game/management/commands/publish_game_events.py](publish_game_events.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 6.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 8.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--group` 기본 village-watch-v1, `--limit` int 기본10. 별도 양수 guard는 없다.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 12.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** group 구독/earliest/자동commit 끔. limit까지 poll하고 빈 batch면 종료한다. value JSON과 key UTF8는 deserializer에서 해석한다.
- **직접 호출:** `KafkaConsumer` → `poll(timeout_ms=2000,max_records=remaining)` → `stdout.write(json.dumps(...))` → batch 처리 뒤 `consumer.commit()`.
- **반환·상태:** event_id/event_type/player_id/key/topic/partition/offset과 observed 수를 출력한다. group offset은 수동 commit으로 변경한다. KeyboardInterrupt를 처리하고 finally close(autocommit=False); DB는 읽지도 않는다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
