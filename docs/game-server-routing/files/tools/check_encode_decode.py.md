# `tools/check_encode_decode.py`

## 책임과 경계

DB export의 첫 번째 비어 있지 않은 사실을 parser로 읽고 JSON UTF-8 왕복 결과를 비교한다.

## 진입점과 실행 흐름

1. 설정된 `DATA_DIR/raw/game-events.jsonl`을 bytes로 연다. 비어 있으면 안내만 출력한다.
2. 첫 비어 있지 않은 줄을 `game.transforms.parse_game_event`로 해석하고 event_id·event_type·player_id·payload 필드를 출력한다.
3. JSON encode 후 같은 parser로 다시 읽어 event_id·payload·event_time 일치 여부를 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

Django settings가 먼저 초기화된 실행 환경이 필요하다. 자체 `django.setup()`이나 CLI 진입 함수는 없으며 import 시에도 최상위 코드가 실행된다. 전체 파일 검증기는 아니다.

## 연결 문서

- [`game/transforms.py`](../game/transforms.py.md)
- [`game/management/commands/export_game_events.py`](../game/management/commands/export_game_events.py.md)

[전체 라우팅 목차](../../README.md)
