# `config/settings.py`

## 책임과 경계

Django·Channels·MySQL·Kafka·Spark·광고 gateway 설정의 조립점이다. 게임 로직과 인증 키를 클라이언트로 내보내지 않는다.

## 값과 데이터 계약

`BASE_DIR`은 game_server 루트, `PROJECT_DIR`은 그 부모, `DATA_DIR`은 `PROJECT_DIR / "data"`이다. `load_dotenv(BASE_DIR / ".env")`는 서비스 시작 시 실행되는 코드이며 이 문서 작성에서는 .env를 열거나 모듈을 import하지 않았다.

| 설정 | 코드가 사용하는 계약 |
| --- | --- |
| `ADS_BASE_URL` | 환경값, 없으면 로컬 8001; 끝 `/` 제거 |
| `ADS_MEDIA_ID`, `ADS_MEDIA_KEY` | 서버의 매체 식별자·인증 키; 키 값은 문서화하지 않음 |
| `DATABASES.default` | MySQL, 필수 `DB_NAME`·`DB_USER`·`DB_PASSWORD`, 선택 `DB_HOST`·`DB_PORT`, utf8mb4 |
| `KAFKA_BOOTSTRAP_SERVERS` | 필수 환경 문자열을 `,`로 나눈 목록 |
| `KAFKA_EVENT_TOPIC` | 환경값 또는 `game.events.v1` |
| `KAFKA_GROUP_ID` | 환경값 또는 `village-watch-v1`; watch 명령은 자체 옵션 기본값 사용 |
| `SPARK_SUBMIT` | 필수 환경값 |
| `SPARK_MASTER` | 환경값 또는 로컬 Spark standalone master |
| `KAFKA_PACKAGE`·`DELTA_PACKAGE` | Spark가 로드할 패키지 좌표 |
| `ROOT_URLCONF`·`ASGI_APPLICATION`·`WSGI_APPLICATION` | config.urls / config.asgi.application / config.wsgi.application |
| `CHANNEL_LAYERS.default` | InMemoryChannelLayer; 프로세스 간 공유하지 않음 |
| 인증 middleware | SessionMiddleware → CsrfViewMiddleware → AuthenticationMiddleware 순서 포함 |
| `LOGIN_URL`·redirect | accounts/login/ → 로그인 성공 play/, 로그아웃 accounts/login/ |
| 실행 기본값 | DEBUG=True, ALLOWED_HOSTS=["*"], Asia/Seoul, USE_TZ=True |

`INSTALLED_APPS`에 daphne·channels·game·analytics와 Django 기본 앱을 등록한다. `TEMPLATES`는 앱 template 검색을 켠다. 필수 환경값을 읽는 `os.environ[...]`은 누락 시 KeyError로 시작을 실패시킨다. 비밀값이나 실제 접속 계정은 이 문서의 범위가 아니다.

## 연결

[config/asgi.py](asgi.py.md) · [config/wsgi.py](wsgi.py.md) · [config/urls.py](urls.py.md) · [game/ad_gateway.py](../game/ad_gateway.py.md)

## 함수·클래스 목록

이 파일은 top-level 함수·클래스·메서드를 정의하지 않는다. 위의 모듈 초기화·등록 값이 실행 경계다.

## 확인 범위

2026-10-07 실제 Python 소스를 AST로 읽고 호출 흐름을 대조했다. 서비스 모듈 import, .env 읽기, DB·Kafka 접속 또는 원본 코드 변경을 하지 않았다. 실행 환경의 정상 동작을 보증하는 런타임 테스트 결과와는 구분한다.
