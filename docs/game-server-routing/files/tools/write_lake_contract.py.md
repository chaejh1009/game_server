# `tools/write_lake_contract.py`

## 책임과 경계

선택한 Bronze manifest의 버전·지문과 분석 재처리 정책을 계약 파일에 기록한다.

## 진입점과 실행 흐름

1. 현재 고정 입력 `data/lake/bronze/game/capture-003/manifest.json`을 읽는다.
2. dataset_version과 input_sha256을 manifest에서 가져오고 event_identity/transport_identity·UTC/Asia/Seoul·30일 보존 정책·재생성 대상을 구성한다.
3. `data/contracts/lake-contract.json` 부모를 만들고 UTF-8 JSON을 저장·출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

입력 capture-003과 bronze_uri는 현재 하드코딩되어 있고 CLI 인자가 없다. bronze_uri 문자열의 `\b`는 역슬래시와 b가 아니라 U+0008 backspace 한 문자로 해석되어 bronze 경로를 손상시킨다. JSON 출력에는 이 제어 문자가 `\b`로 escape되어 보인다. URI 읽기나 경로 존재 검증을 하지 않으므로 계약 파일 작성 성공이 사본 경로의 유효성을 뜻하지 않는다. 원본 자동 삭제도 수행하지 않는다.

## 연결 문서

- [`tools/store_bronze.py`](store_bronze.py.md)
- [`tools/copy_bronze.py`](copy_bronze.py.md)
- [`tools/write_layer_contract.py`](write_layer_contract.py.md)

[전체 라우팅 목차](../../README.md)
