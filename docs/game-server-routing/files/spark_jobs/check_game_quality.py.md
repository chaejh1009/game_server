# `spark_jobs/check_game_quality.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

펼친 Bronze를 정상 accepted와 사유별 quarantine으로 나눈다. 오류 자료를 정상 사건으로 보정하지 않는다.

## 소유 값과 입출력

필수 --input/--output. UTC session. 출력 output/accepted와 output/quarantine(각 errorifexists). 추가 parsed_time timestamp, reason string.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ parquet read
→ try_to_timestamp(event_time)
→ 순서대로 schema!=1 unsupported_schema, schema null missing_schema, ID null missing_event_id, room null missing_room, 시각null invalid_time, 허용 외 종류 unknown_action, 종류null missing_action, 나머지 accepted
→ reason별 건수 표시
→ 로컬 accepted 변수는 event_id/room_id/event_type/parsed_time/reason만 골라 방별 건수 표시
→ 실제 저장은 checked.filter(reason==accepted) 전체 열을 accepted에, 나머지를 quarantine에 저장
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/parse_game_bronze.py`](parse_game_bronze.py.md)
- [`spark_jobs/dedup_game_actions.py`](dedup_game_actions.py.md)

## 현재 구현에서 확인할 점

player_id·payload 완전성 또는 event_id 공백/UUID 형식은 이 코드의 guard가 아니다. accepted 변수의 좁은 projection과 실제 accepted 저장 열은 다르며, 후속 dedup에 필요한 업무 열은 저장본에 남는다.
