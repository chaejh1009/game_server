# `analytics/management/commands/summarize_ingest.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

수집 Parquet 전용 요약과 선택 사건 evidence를 Spark에 맡긴다. game-summary.json을 변경하지 않는다.

## 소유 값과 입출력

--data-dir DATA_DIR; --cores1|2 기본2; --event-id 선택 UUID. Spark 작업은 새 Kafka 읽기나 checkpoint 재설정을 하지 않는다.

## 진입과 직접 호출 흐름

```text
manage.py summarize_ingest
→ Command
→ handle
→ spark-submit
→ spark_jobs/summarize_ingest.py.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
data-dir/cores/event-id 등록
→ cores choices 적용.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
guard: master spark:// 아니면 CommandError
→ spark-submit client/executor1/totalcores + Python conf 구성
→ event-id가 있으면 UUID 정규화, ValueError를 CommandError(event-id must be a UUID)로 변환
→ Spark summarize_ingest.py에 data-dir와 선택 ID 전달
→ 환경 Python 두 변수 지정
→ subprocess.run(check=True,cwd=BASE_DIR). 반환 None; 작업 오류는 그대로 전파.
```

## 직접 연결 문서

- [`spark_jobs/summarize_ingest.py`](../../../spark_jobs/summarize_ingest.py.md)
