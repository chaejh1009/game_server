# `analytics/management/commands/run_game_delta.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

기존 Spark 클러스터에 고유 game fact Delta 스트림을 제출한다. 명령 자체가 중복 제거를 구현하지 않는다.

## 소유 값과 입출력

--topic game.actions.v1; --data-dir settings.DATA_DIR; --progress-output 선택. SPARK_SUBMIT/MASTER, KAFKA_PACKAGE, DELTA_PACKAGE, PROJECT_DIR, BASE_DIR, KAFKA_BOOTSTRAP_SERVERS 사용.

## 진입과 직접 호출 흐름

```text
manage.py run_game_delta
→ Command
→ handle
→ spark-submit
→ spark_jobs/game_actions_delta.py.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
topic/data-dir/progress-output 옵션 등록
→ 반환 None.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
data-dir resolve; progress-output이 없으면 data-dir/marts/progress-game-actions.json
→ spark-submit 인수에 client deploy, executor-cores1/total2, Kafka+Delta packages, 현재 sys.executable driver/executor 설정 구성
→ game_actions_delta.py에 data-dir/bootstrap/topic/progress-output 전달
→ 환경 사본의 PYSPARK_PYTHON/PYSPARK_DRIVER_PYTHON 지정
→ subprocess.run(cwd=BASE_DIR, env=env, check=True). 반환 None; 별도 master/file guard·예외 변환은 없다.
```

## 직접 연결 문서

- [`spark_jobs/game_actions_delta.py`](../../../spark_jobs/game_actions_delta.py.md)
