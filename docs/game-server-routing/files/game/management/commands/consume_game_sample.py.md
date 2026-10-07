# `game/management/commands/consume_game_sample.py`

## 책임과 경계

별도 분석 group으로 읽은 사실을 JSONL에 append하고 파일 내구성 확보 뒤 해당 record의 다음 offset을 commit한다.

## 값과 데이터 계약

`--group` day13-analysis-a, `--limit` int6, `--idle-seconds` int10, `--output` 필수.

## 연결

[game/management/commands/inspect_game_offsets.py](inspect_game_offsets.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 11.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 14.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--group` day13-analysis-a, `--limit` int6, `--idle-seconds` int10, `--output` 필수.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 20.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** limit1..100, idle_seconds1..60, group의 day13-analysis- prefix를 검사한다. 한 번에1건 poll하고 연속 유휴 시간이 지나면 종료한다.
- **직접 호출:** `Path.resolve/mkdir/open("a")` → `KafkaConsumer` → `time.monotonic/poll` → envelope Kafka 위치 추가 → `destination.write/flush` → `os.fsync` → `consumer.commit({TopicPartition:OffsetAndMetadata(offset+1,"",-1)})`.
- **반환·상태:** 파일에 kafka_topic/partition/offset/key를 추가한 JSONL을 append한다. 저장/commit 사이 실패로 재실행 중복 행이 가능하다. finally close(autocommit=False), 처리 위치 및 group/processed/output을 stdout에 출력한다. DB 상태는 변경하지 않는다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
