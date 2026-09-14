# Game Server

Django와 Channels로 구성한 수업용 게임 서버입니다. MySQL에 플레이어 상태와 게임 이벤트를 저장하고, 세션 인증을 거친 WebSocket 명령으로 이동과 코인 채집을 처리합니다. 저장된 게임 이벤트는 Kafka로 발행하거나 관찰할 수 있습니다.

## 현재 구현 상태

- 로그인·로그아웃, 방 정보 화면, 내 상태 조회 API
- WebSocket 연결 시 초기 상태 전송 및 이동·채집 명령 처리
- 트랜잭션과 행 잠금(`select_for_update`)을 이용한 상태 변경 및 이벤트 기록
- 플레이어별 `command_id` 중복 확인으로 성공한 명령의 재실행 방지
- 연결별 명령 간격 제한: 0.2초 미만이면 `too_fast` 반환
- 상태 변경과 `GameEvent` 기록을 하나의 트랜잭션으로 처리
- 미발행 `GameEvent`를 Kafka에 발행하고 broker ack 이후 `published_at` 기록
- Kafka 이벤트 관찰 및 최근 이벤트 JSON 샘플 추출용 관리 명령

`/play/`는 현재 사용자와 방 정보를 보여주는 준비 화면입니다. 지도와 이동·채집 조작 UI는 아직 없습니다. 같은 방의 다른 플레이어에게 상태를 방송하는 기능도 구현되어 있지 않습니다.

`analytics` 앱은 기본 골격만 있습니다. HTTP/WebSocket 서버를 실행할 때 Kafka broker에 연결하지는 않지만, 설정을 읽기 위해 `KAFKA_BOOTSTRAP_SERVERS` 환경 변수는 필요합니다. 이벤트 발행·관찰 명령을 실행하려면 해당 Kafka broker가 실행 중이어야 합니다.

## 로컬 실행

프로젝트 루트(`game_server/`)에서 실행합니다. Python 가상환경과 실행 중인 MySQL 서버, 데이터베이스 및 해당 DB 접근 계정이 필요합니다. 로컬 확인에 사용한 Python 버전은 3.12.10입니다. `mysqlclient` 설치 환경에 따라 MySQL 클라이언트 개발 라이브러리와 빌드 도구가 필요할 수 있습니다.

### 1. 의존성 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

주요 의존성은 Django 5.2, Channels 4, Daphne 4, mysqlclient, python-dotenv입니다. 버전 범위는 [requirements.txt](requirements.txt)를 참고하세요.

### 2. 데이터베이스 설정

MySQL에 사용할 데이터베이스를 `utf8mb4` 문자 집합으로 준비하고, 프로젝트 루트에 `.env`를 작성합니다. 기존 파일이 있다면 필요한 값만 수정합니다.

```dotenv
DB_NAME=game_server
DB_USER=game_user
DB_PASSWORD=replace_with_your_password
DB_HOST=127.0.0.1
DB_PORT=3306
KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
KAFKA_EVENT_TOPIC=game.events.v1
KAFKA_GROUP_ID=village-watch-v1
```

`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `KAFKA_BOOTSTRAP_SERVERS`는 필수입니다. `DB_HOST`와 `DB_PORT`의 기본값은 각각 `127.0.0.1`, `3306`입니다. `KAFKA_EVENT_TOPIC`의 기본값은 `game.events.v1`입니다. `KAFKA_BOOTSTRAP_SERVERS`에는 여러 broker를 쉼표로 구분해 입력할 수 있습니다. `.env`는 Git 추적 대상에서 제외됩니다.

### 3. 테이블 및 플레이어 생성

```bash
python manage.py migrate
python manage.py create_player --username player01 --room room-01
```

새 계정의 비밀번호는 터미널에서 입력합니다. `--room`을 생략하면 `room-01`을 사용합니다.

- 기존 사용자의 비밀번호와 플레이 상태는 유지합니다.
- 기존 플레이어에게 다른 `--room`을 지정해도 방을 변경하지 않습니다.
- 이 명령으로 방에 새 플레이어를 추가할 때는 방당 20명으로 제한합니다.

게임 접속 계정은 `create_player`로 준비해야 합니다. 일반 사용자나 슈퍼유저만 생성하면 게임에 필요한 `Player` 레코드가 없습니다.

### 4. 서버 시작

```bash
python manage.py runserver 127.0.0.1:8000
```

Daphne가 개발 서버를 제공하며 HTTP와 WebSocket을 함께 처리합니다. 브라우저에서 [로그인 화면](http://127.0.0.1:8000/accounts/login/)을 열고 생성한 계정으로 로그인하면 `/play/`로 이동합니다. 루트 경로 `/`에는 화면이 없습니다.

## 엔드포인트

| 경로 | 방식 | 동작 |
| --- | --- | --- |
| `/accounts/login/` | GET, POST | 로그인 화면 및 세션 생성 |
| `/accounts/logout/` | POST | 로그아웃, CSRF 토큰 필요 |
| `/play/` | GET | 로그인 후 사용자·방 정보 표시 |
| `/api/player/` | GET | 내 상태 JSON 조회, 미인증 시 HTTP 401 |
| `/ws/play/` | WebSocket | 세션 인증 후 초기 상태 전송 및 명령 처리 |
| `/admin/` | HTTP | Django 관리자 사이트, 관리자 계정 별도 필요 |

## WebSocket 명령

로그인한 브라우저의 세션 쿠키로 `/ws/play/`에 연결합니다. 미인증 연결은 코드 `4401`로 종료합니다. 로컬 개발 서버의 주소는 `ws://127.0.0.1:8000/ws/play/`입니다.

각 명령의 `command_id`에는 UUID를 사용합니다. 새로운 동작에는 새 UUID를, 동일한 명령을 재전송할 때는 기존 UUID를 사용합니다.

이동 예시:

```json
{"type":"move","direction":"right","command_id":"8df0e267-682c-4c08-a681-791b13c0c324"}
```

방향은 `up`, `down`, `left`, `right`입니다. 한 번에 한 칸 이동하며 맵 범위는 `0 ≤ x < 20`, `0 ≤ y < 15`입니다. 초기 좌표는 `(0, 0)`입니다.

채집 예시:

```json
{"type":"gather","command_id":"e1d8ed45-c420-4d20-94d9-6a0d470f80ac"}
```

채집은 `(2, 2)`에서만 가능하며 성공할 때마다 코인이 1 증가합니다. 이동과 채집에 성공하면 `version`이 1 증가하고 `GameEvent`가 함께 저장됩니다. 이미 성공한 명령을 재전송하면 상태를 다시 변경하지 않고 현재 상태를 반환합니다.

명령 성공 응답 예시:

```json
{"player_id":1,"type":"state","room_id":"room-01","x":1,"y":0,"coins":0,"version":1,"command_id":"8df0e267-682c-4c08-a681-791b13c0c324"}
```

초기 연결과 HTTP 상태 조회 응답에는 `command_id`가 없습니다. 명령 오류는 `type`, `code`, `command_id` 필드로 반환합니다. 주요 오류 코드는 `object_required`, `too_fast`, `invalid_direction`, `outside_map`, `not_at_gather_tile`, `unknown_action`입니다.

## Kafka 이벤트 파이프라인

게임 명령이 성공하면 플레이어 상태와 `GameEvent`가 같은 트랜잭션에서 저장됩니다. `GameEvent.published_at`이 비어 있는 이벤트만 발행 대상입니다.

### 이벤트 발행

```bash
# 미발행 이벤트를 최대 100건 처리한 뒤 종료
python manage.py publish_game_events --once

# 미발행 이벤트를 계속 감시하고 발행
python manage.py publish_game_events --batch-size 100
```

발행 명령은 `event_time`, `event_id` 순서로 이벤트를 읽고, Kafka의 `acks=all` 응답을 받은 뒤에만 `published_at`을 기록합니다. Kafka 메시지의 key는 `player_id`입니다. `--once`를 사용하면 한 번 읽은 batch만 처리하고 종료합니다.

### 이벤트 관찰

```bash
python manage.py watch_game_events --limit 10
python manage.py watch_game_events --group village-watch-v1 --limit 50
```

관찰 명령은 Kafka 이벤트를 JSON으로 출력하며 플레이어 상태나 `GameEvent`를 변경하지 않습니다. 기본 consumer group은 `village-watch-v1`, 기본 출력 개수는 10건입니다.

Kafka에 발행되는 이벤트 envelope은 다음 형태입니다.

```json
{
  "schema_version": 1,
  "event_id": "uuid",
  "event_type": "player.moved",
  "player_id": 1,
  "room_id": "room-01",
  "event_time": "2026-09-14T12:00:00+09:00",
  "payload": {
    "command_id": "uuid",
    "x": 1,
    "y": 0,
    "coins": 0,
    "version": 1
  }
}
```

`event_type`은 현재 `player.moved`와 `player.gathered`를 사용합니다.

### 이벤트 샘플 저장

```bash
python manage.py export_event_sample
```

가장 최근에 저장된 이벤트 한 건을 프로젝트 상위 디렉터리의 `data/samples/game-event.json`에 저장합니다. 이벤트가 하나도 없으면 먼저 게임에서 이동 또는 채집을 실행해야 합니다.

## 프로젝트 구조

```text
config/                         Django 설정, HTTP·ASGI 라우팅
game/
  models.py                     Player, GameEvent 모델
  services.py                   이동·채집, 중복 명령 확인, 이벤트 저장·직렬화
  consumers.py                  WebSocket 인증 및 명령 수신
  views.py                      준비 화면과 상태 조회 API
  routing.py                    WebSocket 경로
  management/commands/          플레이어 생성, 이벤트 발행·관찰·샘플 추출
  migrations/                   데이터베이스 마이그레이션
  templates/                    로그인 및 준비 화면
analytics/                      분석 앱 기본 골격
manage.py                       Django 관리 명령 진입점
requirements.txt                Python 의존성
```

## 점검 및 개발 범위

```bash
python manage.py check
python manage.py test
```

현재 `game/tests.py`와 `analytics/tests.py`에는 테스트 케이스가 없습니다. `check`는 Django 설정 점검이며 DB 연결이나 게임 동작까지 검증하지는 않습니다.

현재 설정은 로컬 수업·개발용입니다. `DEBUG=True`, 전체 호스트 허용, 코드에 고정된 `SECRET_KEY`, 메모리 기반 채널 레이어를 사용합니다. 운영 배포 시 설정 분리와 비밀키 관리가 필요하며, 여러 프로세스 사이의 메시지 공유가 필요하면 채널 레이어도 변경해야 합니다. Kafka 발행 명령도 운영 환경에서는 별도 worker 프로세스로 실행하는 구성이 필요합니다.
