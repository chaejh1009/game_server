import json
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.utils import timezone
from kafka import KafkaConsumer, TopicPartition

from game.models import GameEvent

class Command(BaseCommand):
    help = "Read confirmed-event, publisher and Python 행동 변환기 snapshots."

    def add_arguments(self, parser):
        parser.add_argument("--seconds", type=int, default=60)
        parser.add_argument("--topic", default="game.events.v1")
        parser.add_argument("--group", default="village-actions-v1")

    def handle(self, *args, **options):
        seconds = options["seconds"]
        if not 1 <= seconds <= 3600:
            raise CommandError("--seconds must be 1..3600.")
        now = timezone.now()
        cutoff = now - timedelta(seconds=seconds)
        topic = options["topic"]
        group = options["group"]
        consumer = KafkaConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group,
            enable_auto_commit=False,
            request_timeout_ms=15000,
        )
        partitions = []
        try:
            ids = consumer.partitions_for_topic(topic)
            if ids is None:
                raise CommandError(f"No metadata for topic {topic}.")
            topic_partitions = [
                TopicPartition(topic, number) for number in sorted(ids)
            ]
            starts = consumer.beginning_offsets(topic_partitions)
            ends = consumer.end_offsets(topic_partitions)
            for tp in topic_partitions:
                committed = consumer.committed(tp)
                within = (
                    None if committed is None
                    else starts[tp] <= committed <= ends[tp]
                )
                lag = (
                    ends[tp] - committed
                    if committed is not None and within else None
                )
                partitions.append({
                    "topic": topic,
                    "partition": tp.partition,
                    "beginning_offset": starts[tp],
                    "end_offset": ends[tp],
                    "committed_offset": committed,
                    "within_retention": within,
                    "lag": lag,
                })
        finally:
            consumer.close(autocommit=False)
        recent = GameEvent.objects.filter(
            event_time__gte=cutoff,
            event_time__lt=now,
        )
        by_action = list(
            recent.values("event_type")
            .annotate(count=Count("event_id"))
            .order_by("event_type")
        )
        by_room = list(
            recent.values("room_id")
            .annotate(count=Count("event_id"))
            .order_by("room_id")
        )
        pending = GameEvent.objects.filter(published_at__isnull=True)
        first_pending = pending.order_by("event_time").first()
        oldest_pending_age = (
            None if first_pending is None
            else max(0, (now - first_pending.event_time).total_seconds())
        )
        confirmed_count = recent.count()
        published_recent = GameEvent.objects.filter(
            published_at__gte=cutoff,
            published_at__lt=now,
        ).count()

        marts = settings.DATA_DIR / "marts"
        progress_path = marts / "progress-game-actions.json"
        spark_progress = None
        if progress_path.exists():
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            spark_progress = {
                key: progress.get(key) for key in (
                    "id", "runId", "name", "timestamp", "batchId",
                    "numInputRows", "inputRowsPerSecond",
                    "processedRowsPerSecond", "eventTime",
                )
            }
        known_lags = [
            row["lag"] for row in partitions if row["lag"] is not None
        ]
        report = {
            "schema_version": 1,
            "generated_at": now.isoformat(),
            "window_start": cutoff.isoformat(),
            "window_end": now.isoformat(),
            "window_seconds": seconds,
            "confirmed_count": confirmed_count,
            "confirmed_per_second": confirmed_count / seconds,
            "published_recent": published_recent,
            "pending_mark_count": pending.count(),
            "oldest_pending_age_seconds": oldest_pending_age,
            "by_action": by_action,
            "by_room": by_room,
            "kafka": {
                "topic": topic,
                "group_id": group,
                "partitions": partitions,
                "known_lag_sum": sum(known_lags),
                "lag_complete": len(known_lags) == len(partitions),
            },
            "spark_progress": spark_progress,
        }
        marts.mkdir(parents=True, exist_ok=True)
        target = marts / "game-metrics.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(target)
        self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))