# `tools/ws_load.py`

## 책임과 경계

각 계정별 Django 인증 세션과 WS 연결로 교실용 동시 이동 부하를 만들고 실제 응답 RTT·처리율을 저장한다.

## 진입점과 실행 흐름

1. 직접 실행 시 `main()`이 localhost 입력 범위를 검증하고 비밀번호를 대화형으로 받아 `asyncio.run(run_load(...))`를 호출한다.

## `def utc_now()`

timezone-aware UTC 현재 시각을 ISO 문자열로 반환한다.

## `def nearest_rank(values, fraction)`

빈 표본이면 None을 반환한다. 정렬 표본의 ceil(n*fraction)-1 위치를 선택한다. run_load가 0.95를 전달하여 p95를 계산한다.

## `async def csrf_token(session, base_url)`

같은 session으로 GET /api/auth/csrf/를 redirect 없이 요청한다. 200과 비어 있지 않은 csrfToken 문자열을 요구하고 token을 반환한다.

## `async def login(session, base_url, username, password)`

csrf_token→POST /api/auth/login/을 수행한다. Origin/X-CSRFToken과 계정 값을 보낸다. 200/authenticated=true를 요구한다. 로그인 후 token을 갱신해 session header에 넣고 GET /api/player/로 초기 상태를 반환한다.

## `async def read_until(socket, condition, timeout_seconds)`

perf_counter deadline까지 socket 메시지를 읽는다. TEXT JSON 중 condition을 만족한 데이터만 반환한다. close/error는 ConnectionError, 시간 만료는 TimeoutError로 끝낸다.

## `async def run_player(account, password, options, gate, ready, shared)`

계정별 session과 /ws/play/ 연결을 만들고 snapshot 수신 후 ready를 알린다. gate 이후 제한 시간 동안 이동 UUID command_id를 전송하고 자기 state/error 응답만 기다린다. 성공 RTT·시도·오류를 모아 반환하며 finally에서 준비 신호와 열린 연결 수를 정리한다.

## `async def run_load(accounts, password, options)`

0.1초 간격으로 run_player task를 생성하고 모든 task의 준비 신호를 받은 뒤 gate를 연다. 연결 성공 신호 true와 시작 실패 신호 false를 모두 받으며 connected_success는 true 개수다. 실제 측정 경과 시간·합계·RTT 평균/p95·최대 열린 연결을 계산한다. 원시 RTT 배열을 제외한 by_player와 schema_version=1 결과를 임시 파일로 쓴 뒤 출력 파일로 replace한다.

## `def main()`

계정 파일·clients·seconds·interval·base-url·output을 해석한다. 로컬 HTTP origin, clients 1..200, seconds 5..120, interval>=0.5, 충분한 서로 다른 username을 검사한다. getpass로 비밀번호를 받고 run_load를 실행한다.

## 현재 구현에서 확인할 점

플레이어마다 동시에 기다리는 명령은 하나다. 실제 move 명령은 서버의 PlayConsumer→apply_command로 이어져 Player 좌표·version과 GameEvent 원장을 변경한다. 도구는 측정 전후 게임 상태를 복원하지 않는다. profile의 players_per_room=20/asgi_processes=1은 코드에 기록된 전제이며 서버 설정을 조회해 확인한 값은 아니다.

## 연결 문서

- [`game/consumers.py`](../game/consumers.py.md)
- [`game/services.py`](../game/services.py.md)
- [`game/views.py`](../game/views.py.md)
- [`game/management/commands/prepare_load_players.py`](../game/management/commands/prepare_load_players.py.md)
- [`tools/read_load_result.py`](read_load_result.py.md)
- [`analytics/views.py`](../analytics/views.py.md)

[전체 라우팅 목차](../../README.md)
