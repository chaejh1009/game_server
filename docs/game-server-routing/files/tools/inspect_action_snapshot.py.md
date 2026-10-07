# `tools/inspect_action_snapshot.py`

## 책임과 경계

행동 Topic snapshot의 범위·동일 사실 내용·표시 필드 추가 현황을 검사한다.

## 진입점과 실행 흐름

1. 직접 실행 시 `main()`으로 `--input`을 받아 검사 결과를 JSON으로 출력한다.

## `def inspect(source)`

source와 `.manifest.json`을 읽는다. 각 전달의 고정 offset 범위와 `game.actions.v1` topic을 검사한다. 동일 event_id의 외부 사실 필드와 payload를 비교하되 `action_label`만 제외한다. transition은 비교에 남긴다. 실제 행 수와 record_count를 대조하고 고유 사실별 행동 수·중복 전달 수·label/transition 포함 행 수를 반환한다.

## `def main()`

`--input`을 Path로 해석해 `inspect()`를 호출하고 JSON 보고서를 출력한다. 원본과 manifest는 수정하지 않는다.

## 연결 문서

- [`game/management/commands/snapshot_game_actions.py`](../game/management/commands/snapshot_game_actions.py.md)
- [`tools/check_action_handoff.py`](check_action_handoff.py.md)

[전체 라우팅 목차](../../README.md)
