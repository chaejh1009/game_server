# `tools/check_action_handoff.py`

## 책임과 경계

하나의 event_id에 대해 원본 사실과 표시 필드가 추가된 행동 snapshot을 비교한다.

## 진입점과 실행 흐름

1. 직접 실행 시 `main()`이 입력 경로와 UUID를 검증하고 비교 보고서를 출력한다.

## `def matching_rows(path, event_id)`

path의 비어 있지 않은 JSONL 행을 읽어 event_id가 정확히 같은 행들을 list로 반환한다. 파일은 변경하지 않는다.

## `def check(source_path, actions_path, event_id)`

양쪽에서 matching_rows를 호출하고 원본/파생 행이 없으면 거부한다. 원본 중복 내용이 모두 같은지 확인한다. 파생 행에서 Kafka 위치 필드와 payload.action_label만 제외해 원본과 비교한다. label·Topic·player_id 기반 key를 검사하고 원본 보존 여부·출력 위치 목록을 반환한다.

## `def main()`

`--source`, `--actions`, `--event-id`를 받고 UUID 정규화 후 `check()`를 호출해 JSON을 출력한다.

## 현재 구현에서 확인할 점

`KAFKA_FIELDS`는 kafka_topic/partition/offset/key다. transition은 비교에서 제외하지 않으므로 인계 중 값이 바뀌면 실패한다.

## 연결 문서

- [`game/transforms.py`](../game/transforms.py.md)
- [`game/management/commands/snapshot_game_actions.py`](../game/management/commands/snapshot_game_actions.py.md)

[전체 라우팅 목차](../../README.md)
