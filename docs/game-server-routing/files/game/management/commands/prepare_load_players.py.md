# `game/management/commands/prepare_load_players.py`

## 책임과 경계

부하 테스트 계정 묶음을 만들고 공개 account manifest를 내보낸다. 기존 비밀번호를 덮어쓰지 않는다.

## 값과 데이터 계약

`--count` int 기본20, `--prefix` day18_, `--rooms` load18, `--output` 필수.

## 연결

[game/models.py](../../models.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 12.

- **입력·역할:** Django가 파일명으로 찾는 BaseCommand 하위 클래스다.
- **검사·변환:** help 문자열로 명령 목적을 제공하고 아래 add_arguments/handle이 옵션·실행을 담당한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** manage.py의 execute_from_command_line에서 선택된다. HTTP/WS route는 없다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 15.

- **입력·역할:** Django의 argparse parser를 받는다.
- **검사·변환:** `--count` int 기본20, `--prefix` day18_, `--rooms` load18, `--output` 필수.
- **직접 호출:** `parser.add_argument(...)`를 옵션마다 호출한다.
- **반환·상태:** parser 옵션을 등록하고 None을 반환한다. 실제 입출력은 handle에서 수행한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 21.

- **입력·역할:** Django가 전달한 *args, **options를 받는다.
- **검사·변환:** count1..200, 비어 있지 않은 prefix/room prefix/입력 비밀번호를 검사한다. 기존 계정 비밀번호 불일치, 기존 Player의 다른 방 배정, 새 Player 방 정원20은 CommandError다.
- **직접 호출:** `getpass.getpass` → `get_user_model` → `transaction.atomic` → 번호별 `get_or_create/check_password/set_password/save` → `Player.objects.filter/first/count/create` → `Path.resolve/mkdir/write_text/replace` → `stdout.write`.
- **반환·상태:** 20명 단위 room번호를 만들며 새 Player는 (1,1),coins0,version0이다. 계정/Player 변경은 한 DB transaction이며 이후 {schema_version:1,accounts:[username,room_id,player_id]} JSON을 임시파일→replace로 저장한다. 파일 저장 실패까지 DB를 rollback하는 구조는 아니다. 비밀번호는 manifest에 넣지 않는다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
