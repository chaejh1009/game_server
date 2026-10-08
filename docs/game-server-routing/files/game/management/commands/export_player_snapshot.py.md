# `game/management/commands/export_player_snapshot.py`

## 책임과 경계

Player의 공개 상태를 ID 순서로 읽어 `player-snapshot/v1` NDJSON 파일로 내보낸다. Django 관리 명령이며 HTTP·WebSocket 경로는 없다. DB를 수정하거나 Kafka로 발행하지 않는다.

## 값과 데이터 계약

`python manage.py export_player_snapshot --output <경로>`로 실행한다. `--output`은 필수다. 각 행은 `id`, `room_id`, `coins`, `version`, `updated_at`과 `schema_version: "player-snapshot/v1"`, `source_kind: "player-snapshot"`, `captured_at`을 포함한다. 모든 행의 captured_at은 실행 초기에 얻은 같은 ISO 시각이다. updated_at은 시간대를 포함한 ISO 문자열이며 UTC로 별도 변환하지 않는다.

성공 시 stdout에 `path`, `rows`, `sha256`, `schema_version`, `source_kind`, `captured_at`을 JSON으로 출력한다. 빈 조회 결과는 빈 파일을 만들며 stdout의 captured_at은 null이다. sha256은 완성된 파일 바이트의 SHA-256이다.

## 연결

[game/models.py](../../models.py.md) · [manage.py](../../../manage.py.md)

## 함수·클래스 목록

## `Command` · `class Command(BaseCommand)`

소스 기호: `Command` · 정의 줄: 13.

- **입력·역할:** Django가 파일명으로 찾는 관리 명령 클래스다.
- **검사·변환:** help 문자열로 공개 상태 NDJSON 내보내기 목적을 제공한다.
- **직접 호출:** 클래스 선언 자체에 사용자 정의 함수 호출은 없다.
- **반환·상태:** 옵션 등록은 add_arguments, 실제 조회·파일 출력은 handle이 담당한다.

## `def add_arguments(self, parser)`

소스 기호: `Command.add_arguments` · 정의 줄: 16.

- **입력·역할:** Django argparse parser를 받는다.
- **검사·변환:** 필수 `--output` 옵션을 등록한다.
- **직접 호출:** `parser.add_argument("--output", required=True)`.
- **반환·상태:** parser를 갱신하고 None을 반환한다.

## `def handle(self, *args, **options)`

소스 기호: `Command.handle` · 정의 줄: 19.

- **입력·역할:** options의 output을 Path로 만들고 부모 디렉터리를 생성한다. Player를 ID 순으로 공개 다섯 필드만 조회한다.
- **검사·변환:** updated_at이 naive이면 ValueError로 거부한다. 수집 정보와 Player 값을 합쳐 ensure_ascii=False, sort_keys=True인 JSON을 한 행씩 쓴다.
- **직접 호출:** `Path` → `target.parent.mkdir` → `timezone.now().isoformat` → `Player.objects.order_by(...).values(...).iterator()` → `tempfile.NamedTemporaryFile` → `timezone.is_naive` → `updated_at.isoformat` → `json.dumps`/`stream.write` → `temporary_path.read_bytes`/`hashlib.sha256(...).hexdigest()` → `os.replace` → `self.stdout.write`.
- **반환·상태:** 대상과 같은 디렉터리에 임시 파일을 완성하고 체크섬을 계산한 뒤 기존 대상을 교체한다. try 내부의 OSError·TypeError·ValueError·DatabaseError는 임시 파일을 unlink하고 CommandError로 전달한다. 부모 디렉터리 생성과 조회 준비는 try 밖에 있다. 전체 조회를 고정하는 별도 transaction은 없다. 체크섬 계산은 파일 전체를 메모리로 읽는다.

## 확인 범위

2026-10-08 실제 Python 소스와 AST 함수 서명을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 정적 확인이며 런타임 테스트 결과는 아니다.
