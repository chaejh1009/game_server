# `game/ad_events.py`

## 책임과 경계

인증된 게임 사용자의 광고 이벤트 POST bridge다. 요청 subject를 받지 않고 Player identity를 gateway에 넘긴다. 기존 CSRF 정책을 그대로 따른다.

## 값과 데이터 계약

`/api/ads/events/`의 입력 키는 정확히 decision_id/event_type 두 개다. 키의 추가·누락, JSON 파싱 실패, gateway의 로컬 입력 검증 실패는400 `ad_event_rejected`로 반환한다. 허용된 업무 오류 코드만 노출하며 임의 upstream 오류 본문을 전달하지 않는다.

## 연결

[game/urls.py](urls.py.md) · [game/models.py](models.py.md) · [game/ad_gateway.py](ad_gateway.py.md)

## 함수·클래스 목록

## `def ad_event(request)`

소스 기호: `ad_event` · 정의 줄: 12.

- **입력·역할:** POST JSON {decision_id,event_type}; session user를 받는다. subject/media_id 추가 입력은 거부한다.
- **검사·변환:** CSRF middleware에서 먼저403으로 거부할 수 있다. 뷰에 도달하면 require_POST405 → 미인증401 → Player 없음409. dict 여부와 정확한 키 집합을 검사한다. JSON/Unicode/ValueError는400이며 알려진 결정/노출 오류만 보존한다.
- **직접 호출:** `Player.objects.filter(...).first` → `json.loads` → `request_ad_event(player, ...)` → `JsonResponse`.
- **반환·상태:** 성공200 {event_id,event_type,created}와 Cache-Control:no-store. 업무 거절400, AdsUnavailable503. 허용 code는 decision_snapshot_missing/decision_not_found_for_subject/impression_required/decision_id_required/event_type_invalid이며 나머지는 ad_event_rejected다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
