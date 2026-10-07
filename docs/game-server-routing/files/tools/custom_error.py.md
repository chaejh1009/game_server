# `tools/custom_error.py`

## 책임과 경계

사본 경로의 실행 ID 오류를 표현하는 예외 타입을 정의한다.

## 진입점과 실행 흐름

1. import 시 예외 클래스를 선언한다. 경로 검사와 파일 작업은 하지 않는다.

## `InvalidRunIdError` · `class InvalidRunIdError(Exception)`

`Exception`을 상속한다. `__module__ = "builtins"`를 지정하여 예외 표시의 모듈 이름을 바꾼다. 실제 built-in 예외로 등록하는 동작은 없다.

## 연결 문서

- [`tools/local_paths.py`](local_paths.py.md)

[전체 라우팅 목차](../../README.md)
