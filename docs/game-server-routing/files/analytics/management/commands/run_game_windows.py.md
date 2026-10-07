# `analytics/management/commands/run_game_windows.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

Kafka 전달 레코드의 tumbling 또는 sliding 창 작업을 제출한다. 결과 파일 조회 요청과는 분리된 명령이다.

## 소유 값과 입출력

--kind tumbling|sliding 기본tumbling; --topic game.actions.v1; --data-dir DATA_DIR. executor1/total2; Kafka package4.1.3.

## 진입과 직접 호출 흐름

```text
manage.py run_game_windows
→ Command
→ handle
→ spark-submit
→ spark_jobs/game_windows.py.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
kind/topic/data-dir 등록
→ kind의 choices만 CLI 제한.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
data-dir resolve
→ spark-submit client/executor1/total2 + 현재 Python conf + Kafka package 구성
→ game_windows.py에 data-dir/bootstrap/topic/kind 전달
→ 환경 사본의 Python 두 변수 지정
→ subprocess.run(check=True,cwd=BASE_DIR). 반환 None; master 존재·입력 topic·작업 오류를 별도로 변환하지 않는다.
```

## 직접 연결 문서

- [`spark_jobs/game_windows.py`](../../../spark_jobs/game_windows.py.md)
