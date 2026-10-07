# `tools/read_load_result.py`

## 책임과 경계

저장된 WS 부하 결과의 주요 수치와 방별 연결 성공·명령 성공 수를 출력한다.

## 진입점과 실행 흐름

1. 위치 인자로 결과 JSON 경로를 받아 읽는다. generated_at·연결/시도/성공/오류·경과 시간·처리율·RTT 지표를 출력한다.
2. by_player를 room_id로 묶는다. connected=true인 행만 players에 더하고 success_count를 합산해 방별로 출력한다.

## 함수·클래스

직접 선언한 함수·클래스는 없다. 위의 최상위 실행문이 파일의 실행 경로다.

## 현재 구현에서 확인할 점

부하나 네트워크 요청을 새로 실행하지 않는다. players는 이 측정에서 연결 성공한 계정 수이며 DB의 전체 플레이어 수가 아니다.

## 연결 문서

- [`tools/ws_load.py`](ws_load.py.md)
- [`analytics/views.py`](../analytics/views.py.md)

[전체 라우팅 목차](../../README.md)
