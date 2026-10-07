# `game/apps.py`

## 책임과 경계

INSTALLED_APPS의 game 앱 메타데이터다. HTTP/WS 핸들러나 ready hook은 정의하지 않는다.

## 값과 데이터 계약

GameConfig.name = "game", default_auto_field = "django.db.models.BigAutoField".

## 연결

[config/settings.py](../config/settings.py.md)

## 함수·클래스 목록

## `GameConfig` · `class GameConfig(AppConfig)`

소스 기호: `GameConfig` · 정의 줄: 4.

- **입력·역할:** Django가 앱 설정을 찾을 때 사용하는 AppConfig 하위 클래스다.
- **검사·변환:** 메서드 override나 입력 guard는 없다. name과 기본 자동 PK 유형을 클래스 속성으로 제공한다.
- **직접 호출:** 직접 호출하는 사용자 정의 함수는 없다.
- **반환·상태:** Django 앱 registry에 game의 설정을 제공한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
