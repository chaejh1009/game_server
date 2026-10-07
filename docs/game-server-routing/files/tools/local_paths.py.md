# `tools/local_paths.py`

## 책임과 경계

Bronze 사본의 실행 ID·허용 파일명을 검증해 Path만 반환한다. 파일 I/O는 호출자가 한다.

## 진입점과 실행 흐름

1. 직접 실행할 때만 `--run-id`를 받고 두 사본 경로와 layout_version=v1을 출력한다.

## `def copy_path(run_id, filename)`

run_id에서 하이픈을 뺀 문자열이 영숫자가 아니면 `InvalidRunIdError`를 낸다. filename이 `events.ndjson`/`manifest.json`이 아니면 `ValueError`를 낸다. `Path("data/copies/bronze/game") / run_id / filename`을 반환한다.

## 연결 문서

- [`tools/custom_error.py`](custom_error.py.md)
- [`tools/copy_bronze.py`](copy_bronze.py.md)

[전체 라우팅 목차](../../README.md)
