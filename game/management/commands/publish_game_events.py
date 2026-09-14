import json
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from kafka import KafkaProducer
from game.models import GameEvent
from game.services import serialize_event

class Command(BaseCommand):
    help = "확정 이벤트를 발행하고 ack 뒤 published_at을 기록합니다."
    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true")
        parser.add_argument("--batch-size", type=int, default=100)

    def handle(self, *args, **options):
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            acks="all",
            enable_idempotence=True,
            key_serializer=lambda value: str(value).encode("utf-8"),
            value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
        )
        try:
            while True:
                rows = list(GameEvent.objects.filter(published_at__isnull=True)
                    .order_by("event_time", "event_id")[:options["batch_size"]])
                for event in rows:
                    envelope = serialize_event(event)
                    metadata = producer.send(
                        settings.KAFKA_EVENT_TOPIC,
                        key=event.player_id,
                        value=envelope,
                    ).get(timeout=10)
                    GameEvent.objects.filter(
                        event_id=event.event_id, published_at__isnull=True
                    ).update(published_at=timezone.now())
                    self.stdout.write(
                        f"event={event.event_id} key={event.player_id} "
                        f"partition={metadata.partition} offset={metadata.offset}"
                    )
                if options["once"]:
                    break
                if not rows:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.stdout.write("publisher를 정상 종료합니다.")
        finally:
            producer.close(timeout=10)