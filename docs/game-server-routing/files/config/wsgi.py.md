# `config/wsgi.py`

## 책임과 경계

HTTP 전용 WSGI 진입점이다. WebSocket 라우터를 조립하지 않는다.

## 값과 데이터 계약

`DJANGO_SETTINGS_MODULE` 기본값 → `get_wsgi_application()` → 모듈의 `application`에 바인딩한다.

## 연결

[config/settings.py](settings.py.md) · [config/urls.py](urls.py.md)

## 함수·클래스 목록

이 파일은 top-level 함수·클래스·메서드를 정의하지 않는다. 위의 모듈 초기화·등록 값이 실행 경계다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
