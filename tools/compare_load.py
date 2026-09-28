import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("left")
parser.add_argument("right")
options = parser.parse_args()

reports = [
    json.loads(Path(path).read_text(encoding="utf-8"))
    for path in [options.left, options.right]
]
for path, report in zip([options.left, options.right], reports):
    profile = report["profile"]
    print("file:", path)
    print("clients:", profile["clients"])
    print("interval_seconds:", profile["interval_seconds"])
    print("requested_seconds:", profile["seconds"])
    print("observed_seconds:", round(report["elapsed_seconds"], 3))
    print("connected_peak:", report["connected_peak"])
    print("success_count:", report["success_count"])
    print("error_count:", report["error_count"])
    print("success_per_second:", round(report["success_per_second"], 3))
    print("rtt_p95_ms:", report["rtt_p95_ms"])

same_interval = (
    reports[0]["profile"]["interval_seconds"]
    == reports[1]["profile"]["interval_seconds"]
)
same_duration = (
    reports[0]["profile"]["seconds"]
    == reports[1]["profile"]["seconds"]
)
print("same_interval:", same_interval)
print("same_requested_duration:", same_duration)