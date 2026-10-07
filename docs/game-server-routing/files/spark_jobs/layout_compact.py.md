# `spark_jobs/layout_compact.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

payload를 제외하고 열 순서를 맞춘 뒤 처리 partition을 줄여 Snappy Parquet을 쓰고 전후 행 차이를 검사한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. columns=payload 제외 사전식 정렬; 실제 coalesce(3); output errorifexists.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Parquet read/select(*columns)
→ coalesce(3).write compression snappy
→ 다시 읽기/select 같은 열
→ missing=before.exceptAll(after).count
→ extra=after.subtract(before).count
→ 전후 행수/파일수/missing/extra 출력
→ missing 또는 extra면 ValueError
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/layout_smallfiles.py`](layout_smallfiles.py.md)
- [`spark_jobs/layout_benchmark.py`](layout_benchmark.py.md)

## 현재 구현에서 확인할 점

현재 주석의 최대 두 partition·양방향 exceptAll과 달리 실제 코드는 coalesce(3), 역방향 subtract다. subtract는 중복 수 차이를 보존하지 않아 추가 중복 행 검출의 완전한 양방향 다중집합 검사가 아니다. 저장 후 검사를 수행한다.
