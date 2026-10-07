# `tools/lake_inventory.py`

## 책임과 경계

저장된 화면 집계와 분석 재생성 원천·게임 상태 소유 저장소를 계약 JSON으로 기록한다.

## 진입점과 실행 흐름

1. 작업 폴더 기준 `../data/marts/game-summary.json`을 읽는다.
2. serving path/event_count/rebuildable, game.actions.v1 event_id와 topic/partition/offset 구분, MySQL game_player 상태 소유권을 만든다.
3. `../data/contracts/lake-inventory.json`의 부모를 만들고 JSON을 저장·출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

rebuildable=true는 기록된 전제다. Kafka 보존 범위나 실제 재처리 성공을 이 스크립트가 검증하지 않는다. 네트워크와 DB에 접속하지 않는다.

## 연결 문서

- [`tools/write_lake_contract.py`](write_lake_contract.py.md)
- [`spark_jobs/publish_game_summary.py`](../spark_jobs/publish_game_summary.py.md)

[전체 라우팅 목차](../../README.md)
