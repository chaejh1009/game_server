# `spark_jobs/layout_smallfiles.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

처리 partition 수에 따른 실제 출력 파일수·행수·시간을 비교한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. 요청 partition=[2,5,20]; 경로 output/tasks-<n>; 쓰기 mode=overwrite. stdout result requested_tasks/actual_files/rows.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Parquet read
→ 각 2/5/20에 대해 perf_counter
→ repartition(n).write.overwrite.parquet
→ 재읽기
→ len(inputFiles), count 기록
→ 저장·읽기·count 전체 경과시간 별도 stdout
→ 결과 JSON stdout
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/layout_compact.py`](layout_compact.py.md)

## 현재 구현에서 확인할 점

주석의 2개·20개와 달리 5도 실행한다. overwrite이므로 같은 tasks-n 경로를 재실행하면 기존 비교 결과가 교체된다. actual_files는 요청 partition 수와 별도 관찰값이다.
