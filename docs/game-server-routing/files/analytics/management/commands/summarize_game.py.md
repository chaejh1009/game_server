# `analytics/management/commands/summarize_game.py`

[분석 흐름과 원천 계약](../../../../analytics-overview.md)

## 책임과 경계

raw DB 내보내기 또는 Delta 사실을 선택해 같은 화면용 game-summary 파일로 집계한다.

## 소유 값과 입출력

--source raw|delta 기본raw; --data-dir DATA_DIR; --cores 1|2 기본2. source=delta일 때만 DELTA_PACKAGE 및 Delta session extension/catalog conf를 추가한다.

## 진입과 직접 호출 흐름

```text
manage.py summarize_game
→ Command
→ handle
→ spark-submit
→ spark_jobs/game_batch.py.
```

### `Command` · `class Command(BaseCommand)`

```text
Django BaseCommand 진입 클래스. help를 제공하고 명령행 파싱은 add_arguments, 실행은 handle에 맡긴다. 인스턴스가 별도 분석 상태를 보관하지 않는다.
```

### `Command.add_arguments` · `def add_arguments(self, parser)`

```text
source/data-dir/cores 등록
→ source/cores choices 적용.
```

### `Command.handle` · `def handle(self, *args, **options)`

```text
기본 spark-submit client/executor1/totalcores + 현재 Python conf 구성
→ delta 선택이면 package/extension/catalog 인수 추가
→ game_batch.py에 resolve한 data-dir와 source 전달
→ 환경 사본 Python 두 변수 지정
→ subprocess.run(check=True,cwd=BASE_DIR). 반환 None; 계산은 child Spark 작업이 맡으며 subprocess 오류는 그대로 전파.
```

## 직접 연결 문서

- [`spark_jobs/game_batch.py`](../../../spark_jobs/game_batch.py.md)
