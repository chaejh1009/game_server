# `game/views.py`

## 책임과 경계

게임 상태 HTTP 조회, 세션 로그인, CSRF 발급, 광고 선택 POST와 공개 context GET을 처리한다. 게임 상태 변경은 WebSocket 서비스가 소유한다.

## 값과 데이터 계약

JSON API의 인증 실패는 주로 401이다. @login_required인 play/history는 로그인 URL redirect를 사용한다. require_GET/POST는 method가 다르면 405다. CSRF middleware를 면제하는 데코레이터는 없다.

## 연결

[game/urls.py](urls.py.md) · [game/models.py](models.py.md) · [game/services.py](services.py.md) · [game/ad_gateway.py](ad_gateway.py.md)

## 함수·클래스 목록

## `def player_view(request)`

소스 기호: `player_view` · 정의 줄: 17.

- **입력·역할:** GET request와 session user를 사용한다.
- **검사·변환:** require_GET 후 미인증401. Player를 get하며 Player 없음은 자체 처리하지 않는다.
- **직접 호출:** `Player.objects.get` → `serialize_player` → `JsonResponse`.
- **반환·상태:** 공개 state JSON200 또는 login_required401.

## `def play(request)`

소스 기호: `play` · 정의 줄: 24.

- **입력·역할:** request를 받는 로그인 필요 페이지다.
- **검사·변환:** login_required가 미인증 사용자를 LOGIN_URL로 redirect한다. method 제한 데코레이터는 없다.
- **직접 호출:** `render(request,"game/play.html")`.
- **반환·상태:** 게임 HTML을 반환한다. DB 상태를 변경하지 않는다.

## `def delivery_view(request)`

소스 기호: `delivery_view` · 정의 줄: 28.

- **입력·역할:** GET request/session user를 사용한다.
- **검사·변환:** 미인증401; current user의 player 이벤트만 필터한다.
- **직접 호출:** `GameEvent.objects.filter` → `count` → published_at null `filter().count` → `JsonResponse`.
- **반환·상태:** source=mysql-outbox/event_count/pending_publish_count JSON. 현재 사용자의 Outbox 상태이며 Kafka 소비 완료 수가 아니다.

## `def history(request)`

소스 기호: `history` · 정의 줄: 45.

- **입력·역할:** 로그인 request를 받는다.
- **검사·변환:** login_required를 적용한다. method 제한 데코레이터는 없다. current user 이벤트를 최신20건으로 자른다.
- **직접 호출:** `GameEvent.objects.filter(...).order_by(...)[:20]` → `serialize_event` → `JsonResponse`.
- **반환·상태:** scope=current-player,limit=20,events JSON을 반환한다.

## `def csrf_view(request)`

소스 기호: `csrf_view` · 정의 줄: 57.

- **입력·역할:** GET request를 받는다. 로그인은 요구하지 않는다.
- **검사·변환:** require_GET 및 ensure_csrf_cookie가 적용된다.
- **직접 호출:** `get_token(request)` → `JsonResponse`.
- **반환·상태:** csrfToken JSON과 CSRF cookie 발급을 제공한다. 로그인·광고 POST는 기존 middleware 정책을 따른다.

## `def api_login(request)`

소스 기호: `api_login` · 정의 줄: 64.

- **입력·역할:** POST JSON username/password를 받는다.
- **검사·변환:** JSON/UTF8 오류400 invalid_json. 두 필드가 문자열이 아니면400 missing_credentials. JSON 외곽이 list/null일 때 .get guard는 현재 없다.
- **직접 호출:** `json.loads` → `authenticate` → 성공 시 `auth_login` → `JsonResponse`.
- **반환·상태:** 성공 시 session 로그인 및 authenticated:true200. 인증 실패 authenticated:false401. POST는 CSRF middleware 적용 대상이다.

## `def ad_preview(request)`

소스 기호: `ad_preview` · 정의 줄: 99.

- **입력·역할:** GET request를 받는다.
- **검사·변환:** 로그인 guard 없이 require_GET만 적용된다.
- **직접 호출:** `render(request,"game/ad_preview.html")`.
- **반환·상태:** 광고 확인 HTML을 반환한다. 이 페이지 접근 허용이 광고 decision API의 무인증 조회 허용을 뜻하지 않는다.

## `def ad_decision(request)`

소스 기호: `ad_decision` · 정의 줄: 104.

- **입력·역할:** POST JSON {slot_id}와 인증 session user를 받는다.
- **검사·변환:** 미인증401, Player 없음404. JSON 객체가 아니거나 decode 실패400. slot은 village-board/lobby-banner만 허용한다.
- **직접 호출:** `Player.objects.filter(...).first` → `json.loads` → `request_decision`(내부 context 조회 후 선택) → `JsonResponse`.
- **반환·상태:** 광고 dict200. AdsUnavailable은 ads_unavailable503. 현재 실제 /api/ads/decision/ handler이며 GET은405다. 이 함수는 no-store header를 직접 추가하지 않는다.

## `def ad_context(request)`

소스 기호: `ad_context` · 정의 줄: 125.

- **입력·역할:** GET request와 인증 session user를 받는다. URL 이름은 `game:ad-context`다.
- **검사·변환:** require_GET에서 다른 메서드는405. 미인증401 login_required, Player 없음404 player_missing을 반환한다. subject는 서버에서 Player PK와 ADS_MEDIA_ID로 만든다. 클라이언트 query나 body의 subject는 사용하지 않는다.
- **직접 호출:** `Player.objects.filter(user=request.user).first()` → `request_context(player)` → `JsonResponse`.
- **반환·상태:** `{subject, context}` JSON200에 `Cache-Control: no-store`를 붙인다. AdsUnavailable은503 ads_unavailable로 바꾼다. 오류 응답에는 이 뷰가 no-store를 붙이지 않는다. 게임 상태나 광고 이벤트를 기록하지 않는다.

## 확인 범위

2026-10-13 `fedffd8` 이후 AST 변경 기호와 Git diff의 호출 흐름을 대조했다. 이 정적 대조는 프로젝트 모듈 import나 DB·Kafka·광고 서버 연결 없이 수행했다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
