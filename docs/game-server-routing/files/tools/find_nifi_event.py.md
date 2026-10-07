# `tools/find_nifi_event.py`

## 책임과 경계

NiFi 출력 디렉터리의 제한된 파일 수에서 지정 event_id를 찾아 읽기 전용 증거를 출력한다.

## 진입점과 실행 흐름

1. 직접 실행 시 `main()`을 호출한다. HTTP API나 NiFi 작업 실행기는 아니다.

## `def main()`

`--directory`, `--event-id`, `--max-files`를 받는다. UUID·존재하는 디렉터리·파일 수 1..10000을 검증한다. 정렬한 직계 파일 중 숨김/디렉터리를 건너뛰고 최대 지정 수를 읽는다. 1MiB 초과·읽기/JSON 오류·비객체를 센다. 일치 파일 수와 최대 20개 본문, scan_truncated를 JSON으로 출력한다.

## 연결 문서

- [`game/management/commands/export_game_handoff.py`](../game/management/commands/export_game_handoff.py.md)

[전체 라우팅 목차](../../README.md)
