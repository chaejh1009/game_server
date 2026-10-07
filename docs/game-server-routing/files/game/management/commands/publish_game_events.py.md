# `game/management/commands/publish_game_events.py`

## 책임과 경계

MySQL Outbox의 미발행 확정 사실을 Kafka로 보내고 broker ack 후 published_at을 기록한다.

## 값과 데이터 계약

`--once` store_true, `--batch-size` int 기본100. batch-size의 양수 범위를 별도로 검사하지 않는다.

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

소스 기호: `Command.add_arguments` · 정의 줄: 12.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--once` store_true, `--batch-size` int 기본100. batch-size의 양수 범위를 별도로 검사하지 않는다.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 16.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** published_at null 행을 event_time/event_id 순으로 batch 조회한다. --once면 한 batch 후 종료하고, 대기 행이 없으면 연속 모드에서0.5초 쉰다.
- **직접 호출:** `KafkaProducer(acks="all",enable_idempotence=True)` → `GameEvent.objects.filter/order_by` → `serialize_event` → `producer.send(...).get(timeout=10)` → 조건부 `GameEvent.objects.filter(...).update(published_at=timezone.now())` → `stdout.write`.
- **반환·상태:** key는 player_id UTF8, value는 schema1 envelope이다. ack 뒤에만 DB 발행 시각을 기록한다. ack 후 DB 기록 전 장애는 재전송 가능하므로 애플리케이션 전 구간 exactly-once를 보장하지 않는다. KeyboardInterrupt 안내 후 finally producer.close(10). None 반환.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
