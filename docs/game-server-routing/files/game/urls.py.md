# `game/urls.py`

## 책임과 경계

인증된 게임 HTTP와 광고 bridge의 경로를 등록한다. app_name은 game이며 실제 인증·CSRF·method 판정은 뷰와 middleware가 수행한다.

## 값과 데이터 계약

`urlpatterns`: play/ → play, api/player/ → player_view, api/delivery/ → delivery_view, api/history/ → history, api/auth/csrf/ → csrf_view, api/auth/login/ → api_login, ads-preview/ → ad_preview, api/ads/decision/ → ad_decision, api/ads/events/ → ad_events.ad_event. 이벤트 경로 이름은 `ad-events`이며 namespace를 포함한 reverse 이름은 `game:ad-events`다. 모든 URL은 config의 빈 prefix include 아래이므로 위 문자열이 그대로 루트 경로다.

## 연결

[config/urls.py](../config/urls.py.md) · [game/views.py](views.py.md) · [game/ad_events.py](ad_events.py.md)

## 함수·클래스 목록

이 파일은 top-level 함수·클래스·메서드를 정의하지 않는다. 위의 모듈 초기화·등록 값이 실행 경계다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
