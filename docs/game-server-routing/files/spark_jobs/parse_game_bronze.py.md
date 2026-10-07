# `spark_jobs/parse_game_bronze.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

Kafka 원본 snapshot의 value JSON을 업무 사건 필드로 펼쳐 Bronze Parquet에 저장한다. 품질 판정과 중복 제거는 후속 작업이다.

## 소유 값과 입출력

필수 --input/--output. outer topic/partition/offset/key/value; envelope schema1/event_id/event_type/player_id(string)/room_id/event_time/payload(map<string,string>). UTC session.

## 진입과 직접 호출 흐름

```text
모듈 즉시 CLI
→ SparkSession UTC
→ outer schema JSON read
→ from_json(value,envelope)로 event
→ flat에 Kafka topic/partition/offset/value와 전체 업무 필드 선택
→ 별도 projection(topic/offset/player_id/payload) 5행 미리보기
→ flat.write.mode(errorifexists).parquet(output)
→ spark.stop. 출력 기존경로는 거절; 반환 없음.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/bronze_preview.py`](bronze_preview.py.md)
- [`spark_jobs/check_game_quality.py`](check_game_quality.py.md)
