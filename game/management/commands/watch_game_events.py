import json
from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer

class Command(BaseCommand):
    help = "게임 상태를 바꾸지 않고 Kafka 확정 사실을 읽습니다."
    def add_arguments(self, parser):
        parser.add_argument("--group", default="village-watch-v1")
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.KAFKA_EVENT_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=options["group"],
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=5000,
            key_deserializer=lambda value: value.decode("utf-8") if value is not None else None,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )
        count = 0
        try:
            while count < options["limit"]:
                batches = consumer.poll(timeout_ms=2000, max_records=options["limit"] - count)
                if not batches:
                    break
                for records in batches.values():
                    for record in records:
                        event = record.value
                        self.stdout.write(json.dumps({
                            "event_id": event["event_id"],
                            "event_type": event["event_type"],
                            "player_id": event["player_id"],
                            "key": record.key,
                            "topic": record.topic,
                            "partition": record.partition,
                            "offset": record.offset,
                        }, ensure_ascii=False))
                        count += 1
                consumer.commit()
        except KeyboardInterrupt:
            self.stdout.write("관찰을 마칩니다.")
        finally:
            consumer.close(autocommit=False)
        self.stdout.write(f"observed={count}")