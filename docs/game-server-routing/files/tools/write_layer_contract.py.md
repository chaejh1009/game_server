# `tools/write_layer_contract.py`

## 책임과 경계

Bronze·품질 결과·화면 summary로 Silver/Gold 계층 인계 계약을 작성한다.

## 진입점과 실행 흐름

1. SparkSession을 만들고 `data/lake/quality/parsed-capture-001/quarantine` Parquet의 행 수를 계산한 뒤 stop한다.
2. capture-001 Bronze manifest와 `data/marts/game-summary.json`을 읽는다.
3. 입력 지문·Bronze manifest의 rows·summary의 event_count를 silver_rows로 기록하고 Silver/Gold URI·event_id 중복 제거 키·Asia/Seoul·Gold grain을 구성한다.
4. `data/contracts/layer-contract.json`을 쓰고 출력한다. 부모 폴더를 이 파일에서 만들지는 않는다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

quarantine_rows를 계산하지만 저장하는 contract에는 포함하지 않는다. silver_rows는 summary.event_count에서 가져오며 실제 Silver Parquet의 행 수를 세거나 대조하지 않는다. capture-001 경로는 고정이다. 계층 데이터를 만들거나 dedup을 실행하는 파일은 아니다.

## 연결 문서

- [`spark_jobs/check_game_quality.py`](../spark_jobs/check_game_quality.py.md)
- [`spark_jobs/dedup_game_actions.py`](../spark_jobs/dedup_game_actions.py.md)
- [`spark_jobs/build_game_daily.py`](../spark_jobs/build_game_daily.py.md)
- [`spark_jobs/publish_game_summary.py`](../spark_jobs/publish_game_summary.py.md)

[전체 라우팅 목차](../../README.md)
