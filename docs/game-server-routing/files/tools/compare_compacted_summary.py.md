# `tools/compare_compacted_summary.py`

## 책임과 경계

파일 정리 전후의 화면 집계를 비교한 뒤 compaction 정책을 기록한다.

## 진입점과 실행 흐름

1. `--before`, `--after` JSON을 읽고 event_count·by_action·by_room의 완전 일치를 비교·출력한다.
2. 하나라도 다르면 `SystemExit`로 끝낸다.
3. 통과하면 `data/contracts/compaction-policy.json`에 strategy="write-new-version-then-compare"·snappy·목표 파일 수 3·비교 결과·previous_data_deleted=false를 기록한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

이 파일은 실제 compaction이나 삭제를 수행하지 않는다. 출력 부모 폴더를 만들지 않으므로 contracts 폴더가 먼저 있어야 한다.

## 연결 문서

- [`spark_jobs/layout_compact.py`](../spark_jobs/layout_compact.py.md)
- [`spark_jobs/publish_game_summary.py`](../spark_jobs/publish_game_summary.py.md)

[전체 라우팅 목차](../../README.md)
