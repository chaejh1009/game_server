from django.conf import settings
from game.transforms import parse_game_event
import json

path = settings.DATA_DIR / "raw" / "game-events.jsonl"
with path.open("rb") as stream:
    raw_line = next(
        (line for line in stream if line.strip()), None
    )
    if raw_line is None:
        print("원본 파일이 비어 있습니다.")
    else:
        parsed = parse_game_event(raw_line)
        print({
            "event_id": parsed["event_id"],
            "event_type": parsed["event_type"],
            "player_id": parsed["player_id"],
            "payload_fields": sorted(parsed["payload"]),
        })



if raw_line is not None:
    encoded = json.dumps(
        parsed, ensure_ascii=False
    ).encode("utf-8")
    restored = parse_game_event(encoded)
    print({
        "same_event_id": parsed["event_id"] == restored["event_id"],
        "same_payload": parsed["payload"] == restored["payload"],
        "same_event_time": parsed["event_time"] == restored["event_time"],
    })