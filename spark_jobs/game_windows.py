import argparse
import json
from pathlib import Path
from pyspark.sql import SparkSession, functions as F

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--bootstrap-servers", required=True)
    parser.add_argument("--topic", default="game.actions.v1")
    parser.add_argument("--kind", choices=["tumbling", "sliding"], default="tumbling")
    args = parser.parse_args()
    data_dir = Path(args.data_dir).resolve()
    spark = (SparkSession.builder.appName(f"game-windows-{args.kind}")
        .config("spark.sql.session.timeZone", "Asia/Seoul")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate())
    print("window kind:", args.kind)
    print("data directory:", data_dir)

    schema = '''schema_version int,event_id string,event_type string,player_id long,
        room_id string,event_time string,payload struct<command_id:string,x:int,y:int,
        coins:long,version:long,action_label:string>'''

    messages = (
        spark.readStream.format('kafka')
        .option('kafka.bootstrap.servers', args.bootstrap_servers)
        .option('subscribe', args.topic)
        .option('startingOffsets', 'earliest')
        .load()
    )

    parsed = messages.select(
        F.col('value').cast('string').alias('raw_value'),
        F.col('topic').alias('kafka_topic'),
        F.col('partition').alias('kafka_partition'),
        F.col('offset').alias('kafka_offset'),
        F.from_json(F.col('value').cast('string'), schema).alias('event_data')
    )
    actions = parsed.select('event_data.*', 'raw_value', 'kafka_topic', 'kafka_partition', 'kafka_offset')

    actions = actions.withColumn(
        'event_time', F.to_timestamp('event_time')
    )

    actions = actions.filter(
        F.col('event_time').isNotNull()
        & F.col('event_id').isNotNull()
        & (F.col('schema_version') == 1)
        & F.col('event_type').isin('player.moved', 'player.gathered', 'player.trained')
    )

    actions.printSchema()
    print('streaming input:', actions.isStreaming)

    timed_actions = actions.withWatermark('event_time', '10 seconds')

    windows = (
        timed_actions
        .groupBy(F.window('event_time', '10 seconds'), 'event_type')
        .count()
    )

    final_windows = windows.select(
        F.lit('tumbling').alias('kind'),
        F.col('window.start').alias('window_start'),
        F.col('window.end').alias('window_end'),
        'event_type',
        'count',
    )

    output = data_dir / 'lake' / 'windows' / 'tumbling'
    checkpoint = data_dir / 'checkpoints' / 'windows' / 'tumbling'
    print('window output:', output)
    print('window checkpoint:', checkpoint)

    query = (
        final_windows.writeStream.format('parquet')
        .outputMode('append')
        .option('path', output.as_uri())
        .option('checkpointLocation', checkpoint.as_uri())
        .queryName('game-windows-tumbling')
        .trigger(processingTime='5 seconds')
        .start()
    )
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        pass
    finally:
        query.stop()
        spark.stop()

if __name__ == "__main__":
    main()
