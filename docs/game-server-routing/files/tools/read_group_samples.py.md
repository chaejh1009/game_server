# `tools/read_group_samples.py`

## 책임과 경계

두 consumer group 표본의 고유 event_id 수와 공통 사건 수를 읽는다.

## 진입점과 실행 흐름

1. 최상위 코드가 `../data/group-samples/a.jsonl`과 b.jsonl을 읽어 고유 수와 교집합 수를 출력한다.

## `def read_ids(path)`

path의 비어 있지 않은 JSONL 줄에서 event_id를 읽어 set으로 반환한다. 중복 전달은 이 set에서 합쳐진다.

## 연결 문서

- [`game/management/commands/consume_game_sample.py`](../game/management/commands/consume_game_sample.py.md)

[전체 라우팅 목차](../../README.md)
