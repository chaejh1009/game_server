# `game/admin.py`

## 책임과 경계

Django admin 모듈 자리다. 현재 django.contrib.admin을 import하지만 모델을 register하지 않는다.

## 값과 데이터 계약

등록된 Player/GameEvent ModelAdmin은 없다. `/admin/` 경로 자체의 등록은 config.urls가 담당한다.

## 연결

[config/urls.py](../config/urls.py.md) · [game/models.py](models.py.md)

## 함수·클래스 목록

이 파일은 top-level 함수·클래스·메서드를 정의하지 않는다. 위의 모듈 초기화·등록 값이 실행 경계다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
