# `tools/check_bronze.py`

## 책임과 경계

사본 bytes를 원본 manifest의 bytes·sha256·rows와 비교한다.

## 진입점과 실행 흐름

1. `--data`, `--manifest`를 받고 두 파일을 읽는다.
2. `len(raw)`, `hashlib.sha256(raw).hexdigest()`, `len(raw.splitlines())`를 observed로 계산한다.
3. 세 값이 manifest와 모두 같은지 출력한다. 하나라도 다르면 `SystemExit`로 실패한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

현재 rows 계산은 빈 줄도 센다. `store_bronze.py`는 비어 있지 않은 줄만 세므로 빈 줄이 있는 원본에서는 다른 두 값이 같아도 rows 검사가 실패할 수 있다. 주석의 “빈 줄을 뺀 행 수”와 실제 식을 구분한다.

## 연결 문서

- [`tools/store_bronze.py`](store_bronze.py.md)
- [`tools/copy_bronze.py`](copy_bronze.py.md)

[전체 라우팅 목차](../../README.md)
