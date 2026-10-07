# `tools/check_replay_file.py`

## 책임과 경계

snapshot JSONL의 전달 위치와 manifest의 고정 범위·행 수를 비교한다.

## 진입점과 실행 흐름

1. `../data-replay/raw/game-events.jsonl`과 같은 이름의 `.manifest.json`을 읽는다.
2. 각 행의 kafka_partition별 `start_inclusive <= kafka_offset < end_exclusive`와 topic 일치를 assert한다.
3. 비어 있지 않은 행 수가 record_count와 같은지 assert하고 고유 event_id 수·중복 전달 수를 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

최상위 실행 스크립트이며 `assert`를 사용한다. Python 최적화 모드에서는 assert 검사가 생략된다. replay를 실행하거나 게임 DB를 변경하지 않는다.

## 연결 문서

- [`game/management/commands/snapshot_game_actions.py`](../game/management/commands/snapshot_game_actions.py.md)
- [`tools/inspect_action_snapshot.py`](inspect_action_snapshot.py.md)

[전체 라우팅 목차](../../README.md)
