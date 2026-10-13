# `game/ad_gateway.py`

## 책임과 경계

게임 인증 사용자·Player를 매체 subject로 바꾸고 서버 간 광고 HTTP 요청에 인증 header를 붙인다. 게임 cookie·비밀번호를 광고 서버에 넘기지 않는다.

## 값과 데이터 계약

subject는 `{media_id: settings.ADS_MEDIA_ID, subject_id: str(player.pk)}` 객체다. UUID decision_id는 광고 결정의 식별자이며 Player ID 또는 campaign ID와 교환할 수 없다. `X-Media-ID`와 `X-Media-Key`는 두 gateway 호출 모두 서버에서 붙인다. `call_ads`의 timeout은 3초이며 `request_context`와 `request_decision`의 HTTP 호출은 각각 1.5초다.

두 선택 경로가 공존한다. `decision` → `media_payload` → `call_ads`는 GET 뷰지만 현재 URL 순서상 가려진다. 실제 POST 선택은 `views.ad_decision` → `request_decision` → `request_context`로 광고 서버의 공개 context를 먼저 조회한 뒤 선택 요청에 넣는다. 이 차이를 임의로 합쳐 설명하지 않는다.

## 연결

[config/urls.py](../config/urls.py.md) · [game/views.py](views.py.md) · [game/ad_events.py](ad_events.py.md) · [game/models.py](models.py.md)

## 함수·클래스 목록

## `def media_payload(user)`

소스 기호: `media_payload` · 정의 줄: 16.

- **입력·역할:** 인증 user를 받는다.
- **검사·변환:** Player를 get하고 player PK를 문자열로 바꾼다. 공개 room/coins/version와 UTC captured_at만 context에 선택한다.
- **직접 호출:** `Player.objects.get` → `str(player.pk)` → `datetime.now(timezone.utc).isoformat()`.
- **반환·상태:** {subject,context} dict를 반환한다. Player 없음 예외는 호출 뷰 wrapper가 처리한다.

## `def call_ads(path, payload)`

소스 기호: `call_ads` · 정의 줄: 30.

- **입력·역할:** 광고 서버 상대 path와 JSON 직렬화 가능한 payload를 받는다.
- **검사·변환:** URL을 조립하고 allow_nan=False JSON bytes, Content-Type 및 두 media header로 POST한다. HTTPError body는 최대65536 bytes만 읽어 알려진 오류 code의 콜론 앞부분만 보존한다.
- **직접 호출:** `Request` → `json.dumps(...).encode` → `urlopen(timeout=3)` → `json.load`; HTTPError일 때 `exc.read(65536)` → `json.loads`.
- **반환·상태:** (status,data) tuple. HTTPError는 실제 status와 whitelist error 또는 ad_request_rejected. URLError/TimeoutError/ValueError는503 ads_unavailable. 요청 객체 생성/직렬화는 try 밖이며 일반 OSError/TypeError를 포괄 처리하지 않는다.

## `def viewer_methods(*allowed)`

소스 기호: `viewer_methods` · 정의 줄: 60.

- **입력·역할:** 허용 method 문자열을 *allowed로 받는 decorator factory다.
- **검사·변환:** 내부 decorate(view)/wrapped(request,*args,**kwargs)가 로그인401을 method405보다 먼저 확인한다. Allow header를 설정한다. view의 Player.DoesNotExist409, ValueError/UnicodeDecodeError400을 처리한다.
- **직접 호출:** `wraps(view)` → 내부 wrapper에서 `view(request,*args,**kwargs)` 또는 `JsonResponse`.
- **반환·상태:** decorator를 반환한다. 중첩 함수는 top-level AST inventory 대상은 아니지만 실행 경계로 문서화했다. CSRF 면제를 하지 않는다.

## `def decision(request)`

소스 기호: `decision` · 정의 줄: 81.

- **입력·역할:** @viewer_methods("GET") request; query slot_id를 받는다.
- **검사·변환:** wrapper의 인증/method guard 후 media_payload에 slot_id를 추가한다. 이 함수 자체 slot whitelist는 없다.
- **직접 호출:** `media_payload` → `request.GET.get` → `call_ads("/api/media/decision/",payload)` → `JsonResponse`.
- **반환·상태:** upstream status/body와 no-store header를 반환한다. 현재 config URL 매칭에서는 game.views.ad_decision에 가려져 도달하지 않는다.

## `AdsUnavailable` · `class AdsUnavailable(Exception)`

소스 기호: `AdsUnavailable` · 정의 줄: 89.

- **입력·역할:** 광고 연결/응답 검증 실패를 표현하는 Exception 하위 클래스다.
- **검사·변환:** 별도 속성·메서드 override는 없다.
- **직접 호출:** 직접 함수 호출은 없다.
- **반환·상태:** 게임 view가 이 예외를503 JSON으로 바꾼다.

## `def request_decision(player, slot_id)`

소스 기호: `request_decision` · 정의 줄: 146.

- **입력·역할:** 인증 사용자에게 연결된 player와 허용 slot_id를 받는다. slot whitelist는 호출 뷰가 검사한다.
- **검사·변환:** media key가 비면 AdsUnavailable. `request_context(player)`로 조회·검증한 context를 media_id+subject+slot_id와 함께 POST한다. 빈 context={}도 허용한다. 응답 dict 검사 후 empty=true 또는 ad=null은 {ad:None}으로 정규화하고, 선택 결과는 slot 일치 검사를 한다.
- **직접 호출:** `request_context(player)` → `Request` → `json.dumps` → `urlopen(timeout=1.5)` → `json.load`; dict 확장으로 기존 이미지/식별 필드를 보존한다.
- **반환·상태:** 선택 dict에 body 기본""와 bid_amount(bid_units fallback)를 추가한다. HTTPError/URLError/TimeoutError/OSError/ValueError/KeyError/TypeError를 AdsUnavailable로 변환한다. context 조회 실패는 선택 요청 전 AdsUnavailable로 전파된다. context 호출과 선택 Request 생성/직렬화는 선택 응답 try 밖이다. decision 저장·노출 기록은 하지 않는다.

## `def request_ad_event(player, decision_id, event_type)`

소스 기호: `request_ad_event` · 정의 줄: 178.

- **입력·역할:** player, decision_id 문자열, event_type(impression/click)을 받는다.
- **검사·변환:** 키 없음은 AdsUnavailable. 빈/128자 초과/비문자열 ID나 잘못된 event_type은 ValueError("invalid_ad_event")이며 이벤트 뷰가400 ad_event_rejected로 변환한다. UUID 형식 검사는 하지 않는다. subject를 Player에서 구성한다. upstream503만 AdsUnavailable, 다른 비200은 whitelist ValueError다.
- **직접 호출:** `call_ads("/api/media/events/",payload)` → 응답 event_id/event_type/created 검증.
- **반환·상태:** event_id가 decision_id+":"+event_type이고 created가 정확한 bool일 때 세 필드만 반환한다. 응답 형태 불일치는 AdsUnavailable. created=False도200 성공이며 중복 접수 뜻이다. 서버 간401/403/404 등의 비200은 게임 bridge에서400 ad_event_rejected로 변환된다.

## `def request_context(player)`

소스 기호: `request_context` · 정의 줄: 222.

- **입력·역할:** 로그인 Player를 사용해 광고 서버에 저장된 공개 context를 조회한다. 현재 MySQL Player 상태를 context로 복사하거나 snapshot을 업로드하지 않는다.
- **검사·변환:** 키가 없으면 AdsUnavailable. `{subject: {media_id, subject_id: str(player.pk)}}`를 POST한다. 응답은 dict, subject는 요청과 같고 context는 dict여야 한다. 빈 context는 허용한다. 비어 있지 않으면 정확히 player_id/room_id/coins/version/updated_at 다섯 키를 요구하며 player_id는 subject_id와 같아야 한다. room_id는 문자열, coins/version은 bool을 제외한 int이며 version은 0 이상이다. updated_at은 시간대가 있는 ISO 문자열이어야 한다.
- **직접 호출:** `Request` → `json.dumps(..., allow_nan=False).encode("utf-8")` → `urlopen(timeout=1.5)` → `json.load` → `datetime.fromisoformat` → `dict(context)`. 대상은 `/api/media/context/`이고 Content-Type/Accept/X-Media-ID/X-Media-Key를 붙인다.
- **반환·상태:** 검사한 context의 새 dict를 반환한다. HTTPError/URLError/TimeoutError/OSError/ValueError/KeyError/TypeError는 try 안에서 AdsUnavailable로 변환한다. Request 생성/직렬화는 try 밖이다. 광고 선택·노출·게임 DB 변경은 하지 않는다.

## 확인 범위

2026-10-13 `fedffd8` 이후 AST 변경 기호와 Git diff의 호출 흐름을 대조했다. 이 정적 대조는 프로젝트 모듈 import나 DB·Kafka·광고 서버 연결 없이 수행했다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
