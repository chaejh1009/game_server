# `analytics/management/commands/capture_ingest_environment.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

현재 설정된 수집 실행 환경을 관찰 파일로 남긴다. Spark를 실행했다는 증거를 생성하는 명령은 아니다.

## 소유 값과 입출력

SPARK_MASTER, SPARK_SUBMIT, KAFKA_BOOTSTRAP_SERVERS, PROJECT_DIR, DATA_DIR를 Django settings에서 읽는다. 결과 DATA_DIR/evidence/day15/environment.json: schema_version=1, evidence_kind=configuration-observation, spark_executed=False; topic=game.actions.v1, Kafka Spark package=4.1.3.

## 진입과 직접 호출 흐름

```text
manage.py capture_ingest_environment
→ Command
→ handle.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 handle에서 설정 관찰을 수행한다. 사용자 정의 add_arguments는 없다.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
guard: SPARK_MASTER가 문자열이고 spark://로 시작하는지 검사, SPARK_SUBMIT을 expanduser/resolve한 실제 파일인지 검사; 아니면 CommandError
→ 대상 상위 폴더 생성
→ datetime.now(UTC), sys.version/executable, platform.platform 및 settings 관찰값을 사전에 담음
→ UTF-8 들여쓰기 JSON+개행을 직접 write_text
→ stdout에 경로 출력. 반환값 None; 기존 관찰 파일을 덮어쓴다. subprocess 호출은 없다.
```
