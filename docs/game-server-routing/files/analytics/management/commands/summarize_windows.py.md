# `analytics/management/commands/summarize_windows.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

확정된 Parquet 창에서 작은 조회용 windows.json을 게시하는 Spark 작업을 제출한다.

## 소유 값과 입출력

--data-dir DATA_DIR; --rows 5|10|20 기본20(종류별 최대 행 수). executor1/total2.

## 진입과 직접 호출 흐름

```text
manage.py summarize_windows
→ Command
→ handle
→ spark-submit
→ spark_jobs/summarize_windows.py.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
data-dir/rows 등록
→ rows는 choices로 제한.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
data-dir resolve
→ spark-submit client/executor1/total2/Python conf 구성
→ summarize_windows.py에 data-dir/rows 전달
→ 환경 Python 두 변수 지정
→ subprocess.run(check=True,cwd=BASE_DIR). OSError 또는 CalledProcessError는 CommandError("Window summary did not complete; preserve the previous JSON.")로 변환. 반환 None.
```

## 직접 연결 문서

- [`spark_jobs/summarize_windows.py`](../../../spark_jobs/summarize_windows.py.md)
