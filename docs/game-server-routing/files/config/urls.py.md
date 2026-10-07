# `config/urls.py`

## 책임과 경계

최상위 HTTP 라우터다. urlpatterns는 위에서부터 경로를 찾으며 뷰의 허용 HTTP method는 URL 매칭 뒤 검사한다.

## 값과 데이터 계약

등록 순서는 `admin/` → `accounts/` → 빈 prefix `include("game.urls")` → `api/analytics/` include → analytics actions/metrics/load 직접 경로 → `api/ads/decision/`의 `ad_gateway.decision`이다.

**실제 우선순위:** game.urls 안에 같은 `api/ads/decision/`가 먼저 있으므로 요청 method와 무관하게 `views.ad_decision`으로 resolve된다. GET은 그 뷰의 `@require_POST`에서 405로 끝난다. 아래에 등록된 GET용 `ad_gateway.decision`으로 다시 탐색하지 않는다. `game:ad-decision`과 루트 `ad-decision`이라는 다른 reverse 이름이 있어도 두 URL 문자열은 같다.

analytics 직접 경로 앞에는 analytics.urls include가 있으므로 그 하위 경로가 먼저 매칭될 수 있다. analytics 하위 라우트의 상세 계약은 별도 analytics 문서 범위다.

## 연결

[game/urls.py](../game/urls.py.md) · [game/views.py](../game/views.py.md) · [game/ad_gateway.py](../game/ad_gateway.py.md)

## 함수·클래스 목록

이 파일은 top-level 함수·클래스·메서드를 정의하지 않는다. 위의 모듈 초기화·등록 값이 실행 경계다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
