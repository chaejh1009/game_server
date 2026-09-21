import argparse
import json
from pathlib import Path
from uuid import UUID


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--max-files", type=int, default=2000)
    args = parser.parse_args()
    event_id = str(UUID(args.event_id))
    if not 1 <= args.max_files <= 10000:
        parser.error("max-files must be between 1 and 10000")
    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        parser.error("NiFi output directory does not exist")
    scanned = 0
    malformed = 0
    matching_count = 0
    matches = []
    truncated = False
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if scanned >= args.max_files:
            truncated = True
            break
        scanned += 1
        if path.stat().st_size > 1024 * 1024:
            malformed += 1
            continue
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            malformed += 1
            continue
        if not isinstance(event, dict):
            malformed += 1
            continue
        if event.get("event_id") == event_id:
            matching_count += 1
            if len(matches) < 20:
                matches.append({"filename": path.name, "event": event})
    print(json.dumps({
        "schema_version": 1,
        "requested_event_id": event_id,
        "scanned_files": scanned,
        "unreadable_or_nonobject_files": malformed,
        "scan_truncated": truncated,
        "matching_files": matching_count,
        "returned_matches": len(matches),
        "matches": matches,
        "scope": "bounded-read-of-nifi-output",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()