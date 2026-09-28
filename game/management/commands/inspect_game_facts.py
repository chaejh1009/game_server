import json
from django.core.management.base import BaseCommand
from game.models import GameEvent

class Command(BaseCommand):
    help = "공개 확정 사실의 식별자와 전달 여부를 제한된 행 수로 읽습니다."

    def add_arguments(self, parser):
        parser.add_argument("--rows", type=int, choices=[3, 5, 10], default=5)

    def handle(self, *args, **options):
        events = GameEvent.objects.order_by("-event_time", "-event_id")[:options["rows"]]
        for event in events:
            row = {
                "event_id": str(event.event_id),
                "command_id": event.payload.get("command_id"),
                "player_id": event.player_id,
                "event_type": event.event_type,
                "room_id": event.room_id,
                "event_time": event.event_time.isoformat(),
                "published_at": event.published_at.isoformat() if event.published_at else None,
                "payload_keys": sorted(event.payload.keys()),
                "has_transition": isinstance(event.payload.get("transition"), dict),                
            }
            self.stdout.write(json.dumps(row, ensure_ascii=False))
        totals = {
            "kind": "delivery_summary",
            "confirmed_count": GameEvent.objects.count(),
            "pending_publish_count": GameEvent.objects.filter(published_at__isnull=True).count(),
        }
        self.stdout.write(json.dumps(totals, ensure_ascii=False))