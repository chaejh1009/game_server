# `tools/capture_game.py`

## 책임과 경계

Kafka `game.actions.v1`의 현재 파티션 범위를 고정해 원문 전달 기록을 NDJSON으로 수집한다. 게임 상태와 consumer group commit을 변경하지 않는다.

## 진입점과 실행 흐름

1. 프로젝트 `.env`에서 Kafka 접속 설정을 로드한 뒤 `--output`을 받는다. 자동 commit을 끈 Consumer를 만든다.
2. 각 파티션의 low/high watermark를 한 번 읽어 low로 직접 assign한다. `[low, high)`에서 high는 미포함 끝이다.
3. poll한 원문의 topic·partition·offset·key·value를 기록한다. 고정 high 직전까지 도달한 파티션을 완료 처리한다.
4. 모든 파티션 완료 후 `.ndjson.tmp`를 출력 경로로 교체한다. poll 지연/오류는 실패하며 `finally`에서 Consumer를 닫는다. 행 수와 범위를 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

게임 사실 JSONL과 달리 `value`가 JSON 문자열인 전달 envelope다. 다음 단계는 `store_bronze.py`이며 `game.transforms.parse_game_event`에 전체 envelope를 바로 넘기지 않는다.

## 연결 문서

- [`tools/store_bronze.py`](store_bronze.py.md)
- [`game/management/commands/snapshot_game_actions.py`](../game/management/commands/snapshot_game_actions.py.md)

[전체 라우팅 목차](../../README.md)
