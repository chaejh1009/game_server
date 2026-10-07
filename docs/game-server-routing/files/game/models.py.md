# `game/models.py`

## 책임과 경계

현재 플레이 상태와 확정 사실 Outbox의 영속 모델이다. 광고 decision/event는 이 MySQL 모델에 저장하지 않는다.

## 값과 데이터 계약

`Player.user`는 인증 사용자와 OneToOne(CASCADE), room_id 기본 room-01, x/y/coins/version 기본 0, updated_at은 auto_now이다. 자동 PK는 settings의 BigAutoField다.

`GameEvent.event_id`는 UUID PK(default uuid4), event_type 문자열, player FK(PROTECT), room_id/event_time/payload, nullable published_at을 갖는다. `published_at is null`은 Kafka 발행 대기이며 광고 노출 여부를 뜻하지 않는다.

## 연결

[game/services.py](services.py.md) · [game/management/commands/publish_game_events.py](management/commands/publish_game_events.py.md)

## 함수·클래스 목록

## `Player` · `class Player(models.Model)`

소스 기호: `Player` · 정의 줄: 7.

- **입력·역할:** Django ORM의 Player 모델 클래스다. 인증 사용자별 상태 한 행을 소유한다.
- **검사·변환:** OneToOne로 같은 user의 여러 Player를 제한한다. 좌표 범위·방 정원은 이 모델 필드 검증이 아니라 서비스/생성 명령의 책임이다.
- **직접 호출:** `models.OneToOneField`, `CharField`, `IntegerField`, `DateTimeField`로 schema를 선언한다.
- **반환·상태:** DB 행의 상태는 이동/채집/수련 시 services.apply_command에서 변경한다.

## `def __str__(self)`

소스 기호: `Player.__str__` · 정의 줄: 16.

- **입력·역할:** 입력은 Player 인스턴스 self다.
- **검사·변환:** 변환·guard 없이 연결된 user를 사용한다.
- **직접 호출:** `self.user.get_username()`.
- **반환·상태:** 사용자 이름 문자열을 반환하며 DB 상태를 바꾸지 않는다.

## `GameEvent` · `class GameEvent(models.Model)`

소스 기호: `GameEvent` · 정의 줄: 19.

- **입력·역할:** 확정 게임 사실을 저장하는 ORM 클래스다.
- **검사·변환:** UUID는 새 행의 기본 식별자이고 player 삭제는 PROTECT로 막는다. command_id 중복 방지는 DB unique 필드가 아닌 apply_command 조회에 구현되어 있다.
- **직접 호출:** `uuid.uuid4`를 default callable로 지정하고 ORM 필드를 선언한다.
- **반환·상태:** 한 게임 명령의 결과 payload와 Kafka 발행 진행 상태 published_at을 저장한다.

## `Meta` · `class Meta`

소스 기호: `GameEvent.Meta` · 정의 줄: 28.

- **입력·역할:** GameEvent 내부 ORM 메타 클래스다.
- **검사·변환:** 추가 guard/메서드는 없다.
- **직접 호출:** `models.Index(fields=["published_at", "event_time"])`.
- **반환·상태:** 발행 대기 조회를 위한 복합 인덱스를 선언한다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
