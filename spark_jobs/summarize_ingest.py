import argparse
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from pyspark.sql import SparkSession, functions as F
from game_ingest import write_json_atomic


# 1. 그룹별 집계 결과를 JSON으로 만들기 위한 보조 함수
#    특정 컬럼 기준으로 groupBy + count를 수행하고,
#    너무 많은 그룹이 생성되는 경우 classroom JSON 크기 제한을 위해 예외를 발생시킨다.
def small_groups(frame, column):
    grouped = frame.groupBy(column).count().orderBy(column).limit(1001).collect()
    if len(grouped) > 1000:
        raise ValueError(f"Too many groups for a classroom JSON: {column}")
    return [{column: row[column], "count": int(row["count"])} for row in grouped]

def main():
    # 2. 실행 인자 처리
    #    --data-dir : 수집된 데이터와 결과 JSON이 저장될 기준 디렉터리
    #    --event-id : 특정 이벤트를 추적하고 싶을 때 선택적으로 전달
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--event-id")
    args = parser.parse_args()
    selected_id = str(UUID(args.event_id)) if args.event_id else None

    # 3. 입력 데이터 경로 확인
    #    Kafka에서 수집한 데이터를 Parquet으로 저장한 디렉터리를 찾는다.
    #    아직 ingestion 결과가 없다면 집계를 수행할 수 없으므로 중단한다.
    data_dir = Path(args.data_dir).resolve()
    source_path = data_dir / "stream" / "game-actions-parquet"
    if not source_path.is_dir():
        raise ValueError("Run game ingestion and observe its output first")

    # 4. Spark 세션 생성
    #    UTC 기준으로 시간대를 통일하고,
    #    실습 환경에 맞게 shuffle partition 수를 2개로 제한한다.
    spark = (
        SparkSession.builder.appName("village-ingest-summary")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )

    rows = None
    unique = None
    try:
        # 5. Parquet 데이터 로드
        #    Kafka에서 수집되어 저장된 전체 레코드를 Spark DataFrame으로 읽고 캐싱한다.
        rows = spark.read.parquet(str(source_path)).cache()

        # 6. 정상 데이터 정제 및 이벤트 중복 제거
        #    parse_status가 valid인 레코드만 추출한다.
        #    이후 event_id 기준으로 중복 이벤트를 제거하여 실제 이벤트 단위 데이터를 만든다.
        valid = rows.where(F.col("parse_status") == "valid")
        unique = valid.dropDuplicates(["event_id"]).cache()

        # 7. 전체 수집 데이터 상태 집계
        #    valid / invalid / unsupported 등 parse_status별 건수를 계산한다.
        statuses = {
            row["parse_status"]: int(row["count"])
            for row in rows.groupBy("parse_status").count().collect()
        }
        record_count = sum(statuses.values())
        valid_count = statuses.get("valid", 0)


        # 8. 실제 이벤트 수 및 중복 레코드 수 계산
        #    전체 정상 레코드 수와 event_id 기준 고유 이벤트 수를 비교하여
        #    중복으로 수집된 레코드 개수를 계산한다.
        event_count = unique.count()

        # 9. 이벤트 발생 시간 범위 계산
        #    고유 이벤트 중 가장 오래된 이벤트와 가장 최근 이벤트 시간을 구한다.
        time_range = unique.agg(
            F.min("event_ts").cast("string").alias("first"),
            F.max("event_ts").cast("string").alias("last"),
        ).first()

        # 10. 확인용 샘플 event_id 추출
        #     전체 이벤트를 모두 JSON에 넣는 대신,
        #     정렬된 event_id 중 최대 10개만 샘플로 남긴다.
        sample_ids = [
            row["event_id"]
            for row in unique.select("event_id").orderBy("event_id").limit(10).collect()
        ]

        # 11. 전체 수집 결과 요약 데이터 생성
        #     전체 레코드 수, 정상/비정상 건수, 중복 건수,
        #     action별/room별 이벤트 수, 시간 범위 등을 하나의 결과 객체로 구성한다.
        result = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "kafka-parquet",
            "basis": "all-collected-records",
            "record_count": record_count,
            "valid_record_count": valid_count,
            "invalid_record_count": statuses.get("invalid", 0),
            "unsupported_record_count": statuses.get("unsupported", 0),
            "event_count": int(event_count),
            "duplicate_record_count": int(valid_count - event_count),
            "by_action": small_groups(unique, "event_type"),
            "by_room": small_groups(unique, "room_id"),
            "event_time_min_utc": time_range["first"],
            "event_time_max_utc": time_range["last"],
            "sample_event_ids": sample_ids,
        }

        # 12. 전체 요약 결과 JSON 저장
        #     marts/stream-summary.json 파일로 안전하게 기록한다.
        write_json_atomic(data_dir / "marts" / "stream-summary.json", result)
        print(f"records={record_count} events={event_count}", flush=True)

        # 13. 특정 event_id가 전달된 경우 상세 추적 수행
        #     전체 레코드 중 해당 event_id를 가진 레코드만 다시 검색한다.
        if selected_id is not None:
            selected = rows.where(F.col("event_id") == selected_id)
            matched_count = selected.count()

            # 14. 해당 이벤트의 Kafka 수집 증거 추출
            #     topic / partition / offset / key / raw_value 등을 포함하여
            #     동일 이벤트가 Kafka에서 어떻게 수집되었는지 확인할 수 있도록 만든다.
            details = selected.select(
                "event_id", "event_type", "player_id", "room_id",
                "kafka_topic", "kafka_partition", "kafka_offset",
                "kafka_key", "parse_status", "raw_value",
            ).orderBy(
                "kafka_topic",
                "kafka_partition",
                "kafka_offset",
            ).limit(20).collect()

            # 15. 특정 이벤트에 대한 evidence JSON 생성
            #     해당 event_id가 실제 Parquet에 몇 건 존재하는지와
            #     Kafka 위치 정보를 함께 기록한다.
            evidence = {
                "schema_version": 1,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "requested_event_id": selected_id,
                "matched_records": int(matched_count),
                "returned_records": len(details),
                "matches": [row.asDict(recursive=True) for row in details],
                "scope": "selected-event-in-collected-parquet",
            }

            # 16. 이벤트별 증거 파일 저장
            #     evidence/day15/event-{event_id}.json 형태로 저장한다.
            target = data_dir / "evidence" / "day15" / f"event-{selected_id}.json"
            write_json_atomic(target, evidence)
            print(f"selected_event_matches={matched_count}", flush=True)

    finally:
        # 17. Spark 캐시 및 세션 정리
        #     캐싱한 DataFrame을 해제하고 Spark 세션을 종료한다.
        if unique is not None:
            unique.unpersist()
        if rows is not None:
            rows.unpersist()
        spark.stop()

if __name__ == "__main__":
    main()