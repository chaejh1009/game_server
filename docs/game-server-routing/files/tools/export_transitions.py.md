# `tools/export_transitions.py`

## 책임과 경계

서버 GameEvent export에서 수동 정책의 전이 행을 검증하고 별도 JSONL·manifest로 인계한다. 학습이나 세계 초기화는 수행하지 않는다.

## 진입점과 실행 흐름

1. 직접 실행 시 `main()`을 호출한다. 원본 경로와 다른 새 출력 이름을 요구한다.

## `def validate_transition(transition)`

TRANSITION_FIELDS 누락과 episode UUID를 검사한다. step은 정확히 int 1..5, 관측 x/y/coins와 reward는 정확히 int여야 한다. move/gather/train 및 move 방향, reward=coins 차이, manual-v1, 정확한 bool 종료 필드를 검사한다. terminated는 항상 false, done/truncated는 step==5여야 한다. 유효하면 값 반환 없이 끝난다.

## `def read_transitions(source)`

원본 JSONL에서 payload.transition 없는 이전 행은 건너뛴다. event UUID와 전이를 검증한 후 envelope와 전이 필드만 투영한다. 같은 event_id의 투영 결과가 다르면 거부하고 같은 투영 결과의 재전달은 센다. 나머지 payload 필드는 이 비교에 포함하지 않는다. player_id/episode_id/step 순 정렬 행과 원본·건너뜀·중복 수를 반환한다.

## `def inspect_episodes(rows)`

player_id/episode_id로 묶어 step을 정렬한다. 중복 step을 거부하고 연속 step의 next_observation→observation 연결을 확인한다. [1,2,3,4,5]이고 마지막 done이면 완성 묶음으로 센다. 전체/완성/부분 episode 수를 반환한다.

## `def main()`

`--input`, `--output`을 절대 경로로 만들고 원본과 출력 동일/기존 출력·manifest 존재를 거부한다. read_transitions→inspect_episodes 후 배타적 생성 모드로 JSONL을 쓴다. counts·policy·episode/termination 규칙·training_performed=false manifest를 저장하고 출력한다.

## 연결 문서

- [`game/services.py`](../game/services.py.md)
- [`game/management/commands/export_game_events.py`](../game/management/commands/export_game_events.py.md)

[전체 라우팅 목차](../../README.md)
