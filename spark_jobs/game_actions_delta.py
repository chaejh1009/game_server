"""Day 17: one confirmed game fact per event_id, separate from raw history."""
import argparse
import json
from pathlib import Path

from pyspark.sql import SparkSession, functions as F


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--bootstrap-servers", required=True)
    parser.add_argument("--topic", default="game.actions.v1")
    parser.add_argument("--progress-output")
    args = parser.parse_args()
    data_dir = Path(args.data_dir).resolve()
    target = (data_dir / "lake" / "silver" / "game_actions").as_uri()
    spark = (
        SparkSession.builder.appName("game-actions-delta")
        .config("spark.sql.session.timeZone", "Asia/Seoul")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


    schema = """schema_version int,event_id string,event_type string,
        player_id long,room_id string,event_time string"""
    kafka = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.bootstrap_servers)
        .option("subscribe", args.topic)
        .option("startingOffsets", "earliest")
        .load()
    )

    actions = (
        kafka.select(
            F.from_json(F.col("value").cast("string"), schema).alias("body"),
            F.col("value").cast("string").alias("raw_value"),
            F.get_json_object(F.col("value").cast("string"), "$.payload").alias("payload_json"),
            F.col("topic").alias("kafka_topic"),
            F.col("partition").alias("kafka_partition"),
            F.col("offset").alias("kafka_offset"),
        )
        .select("body.*", "raw_value", "payload_json", "kafka_topic", "kafka_partition", "kafka_offset")
        .filter(F.col("event_id").isNotNull() & (F.col("schema_version") == 1)
                & F.col("event_type").isin("player.moved", "player.gathered", "player.trained"))
    )

    def save_unique(batch, batch_id):
        unique = batch.dropDuplicates(['event_id'])
        if unique.isEmpty():
            return
        unique.persist()
        try:
            if not (data_dir / 'lake' / 'silver' / 'game_actions' / '_delta_log').exists():
                unique.write.format('delta').mode('errorifexists').save(target)
            else:
                unique.createOrReplaceTempView('incoming_actions')
                # foreachBatch temp views belong to the batch's Spark session.
                batch.sparkSession.sql(f'''
                    MERGE INTO delta.`{target}` AS saved
                    USING incoming_actions AS incoming
                    ON saved.event_id = incoming.event_id
                    WHEN NOT MATCHED THEN INSERT *
                ''')
            print(f'delta batch {batch_id}: unique input facts={unique.count()}')
        finally:
            unique.unpersist()

    checkpoint = data_dir / "checkpoints" / "game-actions-delta-v1"
    progress_path = Path(args.progress_output).resolve() if args.progress_output else data_dir / "marts" / "progress-game-actions.json"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    query = (
        actions.writeStream.foreachBatch(save_unique)
        .outputMode("append")
        .option("checkpointLocation", checkpoint.as_uri())
        .queryName("game-actions-delta-v1")
        .trigger(processingTime="5 seconds")
        .start()
    )
    last_batch_id = None
    try:
        while not query.awaitTermination(5):
            snapshot = query.lastProgress
            progress = (json.loads(snapshot.json) if hasattr(snapshot, "json") else snapshot) if snapshot is not None else None
            if progress and progress["batchId"] != last_batch_id:
                temporary = progress_path.with_suffix(".tmp")
                temporary.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
                temporary.replace(progress_path)
                print("completed delta batch:", progress["batchId"], "input rows:", progress.get("numInputRows"))
                last_batch_id = progress["batchId"]
    except KeyboardInterrupt:
        pass
    finally:
        query.stop()
        spark.stop()

if __name__ == "__main__":
    main()
