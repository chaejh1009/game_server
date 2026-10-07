# `analytics/management/commands/run_game_ingest.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

독립 Kafka→Parquet 수집 작업을 기존 standalone Spark master에 제출한다. 게임 요약이나 Delta 원천과 다른 출력/checkpoint를 유지한다.

## 소유 값과 입출력

--data-dir DATA_DIR; --mode continuous|available-now 기본continuous; --cores 1|2 기본2; --max-offsets1000; --trigger-seconds5. topic은 game.actions.v1로 고정. Kafka package org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.3.

## 진입과 직접 호출 흐름

```text
manage.py run_game_ingest
→ Command
→ handle
→ spark-submit
→ spark_jobs/game_ingest.py.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
data-dir/mode/cores/max-offsets/trigger-seconds 등록
→ mode와 cores는 argparse choices로 제한.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
guard: SPARK_MASTER spark:// prefix, max-offsets와 trigger-seconds 양수, job 파일 존재; 위반 시 CommandError
→ data-dir resolve
→ spark-submit client/executor1/totalcores와 Kafka package, sys.executable conf 구성
→ game_ingest.py에 bootstrap/topic/mode/rate/trigger 전달
→ 환경 사본 Python 두 변수 지정
→ master/script stdout
→ subprocess.run(check=True,cwd=BASE_DIR). KeyboardInterrupt는 보존 안내 출력; CalledProcessError는 종료코드를 담은 CommandError. 반환 None.
```

## 직접 연결 문서

- [`spark_jobs/game_ingest.py`](../../../spark_jobs/game_ingest.py.md)
