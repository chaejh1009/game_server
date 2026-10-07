# `tools/copy_bronze.py`

## 책임과 경계

같은 Bronze 실행의 이벤트와 manifest를 bytes 그대로 로컬 사본 폴더에 복사한다.

## 진입점과 실행 흐름

1. `--run-id`를 받고 `local_paths.copy_path`로 events.ndjson과 manifest.json의 목적지를 계산한다.
2. `data/lake/bronze/game/<run_id>/`에서 두 파일을 모두 읽는다.
3. `data/copies/bronze/game/<run_id>/`가 이미 있으면 중단한다. 새 폴더에 두 bytes를 순서대로 쓴다.
4. 사본 경로·파일 이름·각 byte 수와 합계를 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 연결 문서

- [`tools/local_paths.py`](local_paths.py.md)
- [`tools/store_bronze.py`](store_bronze.py.md)
- [`tools/check_bronze.py`](check_bronze.py.md)

[전체 라우팅 목차](../../README.md)
