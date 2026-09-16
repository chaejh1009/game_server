import json
import os
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from kafka import KafkaConsumer, TopicPartition
from kafka.structs import OffsetAndMetadata

class Command(BaseCommand):
    help = "별도 분석 group의 이벤트를 JSONL에 저장하고 다음 위치를 commit"

    def add_arguments(self, parser):
        parser.add_argument("--group", default="day13-analysis-a")
        parser.add_argument("--limit", type=int, default=6)
        parser.add_argument("--idle-seconds", type=int, default=10)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        limit = options["limit"]
        idle_seconds = options["idle_seconds"]
        group = options["group"]
        if not 1 <= limit <= 100:
            raise CommandError("--limit은 1..100 범위입니다.")
        if not 1 <= idle_seconds <= 60:
            raise CommandError("--idle-seconds는 1..60 범위입니다.")
        if not group.startswith("day13-analysis-"):
            raise CommandError("수업용 day13-analysis- group만 사용합니다.")

        output = Path(options["output"]).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        consumer = KafkaConsumer(
            settings.KAFKA_EVENT_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            key_deserializer=lambda value: (
                value.decode("utf-8") if value is not None else None
            ),
            value_deserializer=lambda value: json.loads(
                value.decode("utf-8")
            ),
        )
        processed = 0
        idle_deadline = time.monotonic() + idle_seconds
        try:
            with output.open("a", encoding="utf-8") as destination:
                while processed < limit:
                    batches = consumer.poll(
                        timeout_ms=500, max_records=1
                    )
                    if not batches:
                        if time.monotonic() >= idle_deadline:
                            break
                        continue

                    for topic_partition, records in batches.items():
                        for record in records:
                            envelope = dict(record.value)
                            envelope["kafka_topic"] = record.topic
                            envelope["kafka_partition"] = record.partition
                            envelope["kafka_offset"] = record.offset
                            envelope["kafka_key"] = record.key
                            destination.write(
                                json.dumps(envelope, ensure_ascii=False)
                                + "\n"
                            )
                            destination.flush()
                            os.fsync(destination.fileno())
                            consumer.commit({
                                TopicPartition(
                                    record.topic, record.partition
                                ): OffsetAndMetadata(
                                    record.offset + 1, "", -1,
                                )
                            })
                            processed += 1
                            idle_deadline = (
                                time.monotonic() + idle_seconds
                            )
                            self.stdout.write(json.dumps({
                                "event_id": envelope["event_id"],
                                "partition": record.partition,
                                "processed_offset": record.offset,
                                "committed_next": record.offset + 1,
                            }, ensure_ascii=False))
        finally:
            consumer.close(autocommit=False)

        self.stdout.write(json.dumps({
            "group": group,
            "processed": processed,
            "output": str(output),
        }, ensure_ascii=False))