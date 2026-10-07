# `spark_jobs/publish_game_summary.py`

[분석 흐름과 원천 계약](../../analytics-overview.md)

## 책임과 경계

고유 Silver에서 작은 화면용 행동·방 집계를 만들어 지정 JSON 파일에 게시한다.

## 소유 값과 입출력

필수 --input/--output; UTC session. summary dataset_version=capture-001, schema_version1, generated_at,event_count,by_action,by_room. 방그룹 한도100.

## 진입과 직접 호출 흐름

```text
즉시 CLI/Spark
→ Silver Parquet
→ event_type/room_id count 정렬
→ rooms.count()>100이면 ValueError("too many stores")
→ 작은 action/room collect/asDict
→ UTC generated_at와 silver.count 포함 summary
→ output.parent 생성
→ output.suffix+.tmp에 UTF-8 indent2 JSON
→ replace(output)
→ stdout
→ spark.stop.
```

이 파일에는 직접 선언한 클래스·함수·메서드가 없다. 위 흐름은 모듈 최상위 실행 순서다.

## 직접 연결 문서

- [`spark_jobs/dedup_game_actions.py`](dedup_game_actions.py.md)
- [`analytics/views.py`](../analytics/views.py.md)

## 현재 구현에서 확인할 점

출력 파일 경로를 DATA_DIR/marts/game-summary.json로 지정하면 summary_view가 읽는다. 이 요약에는 game_batch의 source/record_count 필드가 없고 dataset_version이 추가된다. 입력은 개별 Silver 사건이며 Gold 일별 집계가 아니다.
