# `manage.py`

## 책임과 경계

Django 관리 명령의 프로세스 진입점이다. 게임 규칙이나 Kafka 전송을 직접 구현하지 않고 Django 명령 탐색기에 argv를 넘긴다.

## 값과 데이터 계약

`DJANGO_SETTINGS_MODULE`이 없을 때만 `config.settings`를 지정한다. `sys.argv`는 명령명과 옵션을 유지한다.

## 연결

[config/settings.py](config/settings.py.md)

## 함수·클래스 목록

## `def main()`

소스 기호: `main` · 정의 줄: 7.

- **입력·역할:** 입력 인자는 없으며 `sys.argv`와 프로세스 환경을 읽는다.
- **검사·변환:** settings 기본값을 지정한 뒤 Django import를 시도한다. import 실패는 가상환경 안내를 포함한 ImportError로 다시 올린다.
- **직접 호출:** `os.environ.setdefault` → `execute_from_command_line(sys.argv)`.
- **반환·상태:** 반환값은 None이다. 선택한 명령의 출력·파일·DB/Kafka 변경은 해당 Command가 소유한다. `__main__` 조건에서만 호출한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
