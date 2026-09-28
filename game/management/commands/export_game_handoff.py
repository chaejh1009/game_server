import json
from datetime import datetime, timezone as datetime_timezone
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from game.models import GameEvent


class Command(BaseCommand):
    help = "Export confirmed GameEvent rows as UTF-8 JSON Lines."

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True)
        parser.add_argument("--since")
        parser.add_argument("--until")

    def handle(self, *args, **options):
        query = GameEvent.objects.order_by("event_time", "event_id")
        for name, lookup in [
            ("since", "event_time__gte"), ("until", "event_time__lt")
        ]:
            text = options[name]
            if text:
                moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
                if moment.tzinfo is None:
                    raise CommandError("Use an ISO timestamp with timezone.")
                query = query.filter(**{lookup: moment})
        output = Path(options["output"]).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        count = 0
        with temporary.open("w", encoding="utf-8") as stream:
            for event in query.iterator(chunk_size=1000):
                row = {
                    "schema_version": 1,
                    "event_id": str(event.event_id),
                    "event_type": event.event_type,
                    "player_id": event.player_id,
                    "room_id": event.room_id,
                    "event_time": event.event_time.astimezone(
                        datetime_timezone.utc
                    ).isoformat(),
                    "payload": event.payload,
                }
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1
        temporary.replace(output)
        self.stdout.write(f"events={count} output={output}")