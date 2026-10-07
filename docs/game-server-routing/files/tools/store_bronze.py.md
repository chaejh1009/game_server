# `tools/store_bronze.py`

## 책임과 경계

수집 NDJSON의 원본 bytes와 manifest를 새 Bronze 실행 폴더에 보존한다.

## 진입점과 실행 흐름

1. `--input`, `--run-id`를 받는다. 하이픈을 뺀 run_id가 비어 있지 않은 영숫자인지 확인한다.
2. 원본 bytes를 읽고 비어 있지 않은 각 줄을 JSON으로 해석한다. `data/lake/bronze/game/<run_id>/`를 `exist_ok=False`로 만든다.
3. `events.ndjson`에 bytes를 그대로 기록하고 파티션별 실제 관찰 offset의 min/max를 모은다.
4. `manifest.json`에 rows·bytes·sha256·captured_at·offset_ranges·data_file·source_file_name을 기록하고 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

offset_ranges는 관찰한 최솟값/최댓값이다. Kafka 전체 보존 범위를 뜻하지 않는다. events 기록 뒤 manifest 계산이 실패하면 폴더가 남을 수 있으며 이 스크립트는 rollback하지 않는다.

## 연결 문서

- [`tools/capture_game.py`](capture_game.py.md)
- [`tools/copy_bronze.py`](copy_bronze.py.md)
- [`tools/check_bronze.py`](check_bronze.py.md)

[전체 라우팅 목차](../../README.md)
