import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("path")
options = parser.parse_args()
report = json.loads(Path(options.path).read_text(encoding="utf-8"))

for key in [
    "generated_at", "connected_success", "connected_peak",
    "attempt_count", "success_count", "error_count",
    "elapsed_seconds", "success_per_second",
    "rtt_sample_count", "rtt_mean_ms", "rtt_p95_ms",
]:
    print(key, "=", report[key])
by_room = {}
for row in report["by_player"]:
    room = row["room_id"]
    item = by_room.setdefault(room, {"players": 0, "success_count": 0})
    item["players"] += int(row["connected"])
    item["success_count"] += row["success_count"]

print("by_room")
for room, values in sorted(by_room.items()):
    print(room, values)