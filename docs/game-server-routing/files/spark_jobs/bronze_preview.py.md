# `spark_jobs/bronze_preview.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Kafka bounded snapshot JSON의 전달 위치와 분포를 살펴본다. 변환 결과 파일을 저장하지 않는다.

## 소유 값과 입출력

필수 --input. outer schema: topic/key/value string, partition int, offset long. appName=village-bronze-preview.

## 진입과 직접 호출 흐름

```text
모듈 즉시 argparse
→ SparkSession
→ 명시 outer schema로 JSON 읽기
→ topic/partition/offset 5행 표시
→ partition별 rows/min offset/max offset/countDistinct(key) 집계·정렬 표시
→ 실제 sparkContext.master 출력
→ spark.stop. 반환값·출력파일 없음.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/parse_game_bronze.py`](parse_game_bronze.py.md)
