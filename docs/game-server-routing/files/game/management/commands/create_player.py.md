# `game/management/commands/create_player.py`

## 책임과 경계

새 인증 계정과 Player를 원자적으로 만들고 기존 Player 상태/비밀번호를 보존한다.

## 값과 데이터 계약

`--username` 필수, `--room` 기본 room-01.

## 연결

[game/models.py](../../models.py.md)

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
- **검사·변환:** `--username` 필수, `--room` 기본 room-01.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 18.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** username.strip()가 빈 값이면 CommandError. 새 계정에만 getpass로 비밀번호를 받고 빈 값이면 실패한다. Player가 없는 사용자만 방 정원20을 검사한다.
- **직접 호출:** `get_user_model` → `User.objects.get_or_create` → 새 user의 `getpass/set_password/save` → `Player.objects.filter(...).exists/count` → `Player.objects.get_or_create` → `stdout.write`.
- **반환·상태:** @transaction.atomic 안에서 계정/Player를 만든다. 기존 Player의 room/좌표/coins/version은 유지한다. player_id/생성 여부/상태를 출력하고 None을 반환한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
