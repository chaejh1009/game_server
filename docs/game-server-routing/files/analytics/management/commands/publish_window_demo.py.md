# `analytics/management/commands/publish_window_demo.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

고정 event-time 단계의 합성 분석 레코드를 게임이 소비하지 않는 별도 demo topic에 발행한다. DB GameEvent나 실제 사용자 행동은 만들지 않는다.

## 소유 값과 입출력

--phase 필수 int 1..5. topic=game.actions.window-demo.v1, partition1, replication_factor3, min.insync.replicas2. 고정 UTC 기준시각 2026-09-11T01:00:00+00:00; player999/demo-room, source=synthetic-window-demo.

## 진입과 직접 호출 흐름

```text
manage.py publish_window_demo
→ Command
→ handle.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
parser.add_argument(--phase, type=int, choices=range(1,6), required=True)
→ 잘못된 단계는 CLI 파서가 거절.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
KafkaAdminClient 생성
→ NewTopic 생성 요청, TopicAlreadyExistsError만 무시
→ finally admin.close
→ phase별 (번호,기준초) 목록 선택
→ KafkaProducer(acks=all, UTF-8 key/JSON serializers)
→ event_id=UUID(int=번호), event_type=player.moved, payload 좌표/coins/version/command_id/action_label 및 synthetic source 구성
→ send(topic,key="999",value=row).get(timeout=10)
→ 실제 topic/partition/offset/event_time stdout 출력
→ finally producer.close(timeout=10). 반환 None; 3복제본/ISR2를 충족하는 Kafka 환경이 필요하다.
```
