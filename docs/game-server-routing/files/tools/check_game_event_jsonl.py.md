# `tools/check_game_event_jsonl.py`

## 책임과 경계

고정 경로의 게임 사실 JSONL에서 첫 행의 필드 구성을 확인한다.

## 진입점과 실행 흐름

1. 현재 작업 폴더 기준 `../data-replay/raw/game-events.jsonl`에서 첫 비어 있지 않은 줄을 읽는다.
2. 비어 있으면 집계 수 0 안내를 출력한다. 행이 있으면 필수 6필드와의 차이·event_id·event_type·payload 키를 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

`missing`을 포함한 출력 딕셔너리를 만드는 동안 event_id/event_type/payload를 직접 인덱싱한다. 이 키가 없으면 `print()`가 호출되기 전에 `KeyError`가 나므로 missing 결과도 출력되지 않는다. UUID·시간·전체 파일 유효성은 검사하지 않는다.

## 연결 문서

- [`game/transforms.py`](../game/transforms.py.md)
- [`tools/check_replay_file.py`](check_replay_file.py.md)

[전체 라우팅 목차](../../README.md)
