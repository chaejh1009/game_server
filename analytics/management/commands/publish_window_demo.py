"""Send explicitly synthetic analysis rows to a topic not consumed by the game."""
import json
from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


class Command(BaseCommand):
    help = "Publish one of five deterministic event-time phases to a separate demo topic."

    def add_arguments(self, parser):
        parser.add_argument("--phase", type=int, choices=range(1, 6), required=True)

    def handle(self, *args, **options):
        topic = "game.actions.window-demo.v1"
        admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

        try:
            try:
                admin.create_topics([NewTopic(
                    name=topic, num_partitions=1, replication_factor=3,
                    topic_configs={"min.insync.replicas": "2"},
                )])
            except TopicAlreadyExistsError:
                pass
        finally:
            admin.close()

        phases = {
            1: [(1, 2), (2, 4)],
            2: [(3, 12), (4, 14)],
            3: [(5, 25)],
            4: [(6, 45)],
            5: [(7, 65)],
        }
        base = datetime.fromisoformat("2026-09-11T01:00:00+00:00")
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            acks="all",
            key_serializer=lambda value: value.encode("utf-8"),
            value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
        )
        try:
            for number, second in phases[options["phase"]]:
                timestamp = (base + timedelta(seconds=second)).isoformat()
                row = {
                    "schema_version": 1,
                    "event_id": str(UUID(int=number)),
                    "player_id": 999,
                    "room_id": "demo-room",
                    "event_type": "player.moved",
                    "event_time": timestamp,
                    "payload": {"x": number, "y": 0, "coins": 0, "version": number,
                                "command_id": str(UUID(int=100 + number)), "action_label": "이동"},
                    "source": "synthetic-window-demo",
                }
                result = producer.send(topic, key="999", value=row).get(timeout=10)
                self.stdout.write(json.dumps({
                    "phase": options["phase"], "topic": result.topic,
                    "partition": result.partition, "offset": result.offset,
                    "event_time": timestamp,
                }, ensure_ascii=False))
        finally:
            producer.close(timeout=10)