import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from game.transforms import ACTION_LABELS

@require_GET
def summary_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    path = settings.DATA_DIR / "marts" / "game-summary.json"
    if not path.exists():
        return JsonResponse({"available": False, "reason": "summary_not_created"})
    summary = json.loads(path.read_text(encoding="utf-8"))
    return JsonResponse({"available": True, **summary})

@login_required
def actions_snapshot(request):
    root = settings.DATA_DIR.parent / "data-replay" / "actions"
    summary_path = root / "marts" / "game-summary.json"
    manifest_path = root / "raw" / "game-events.manifest.json"
    if not summary_path.exists() or not manifest_path.exists():
        return JsonResponse({
            "available": False,
            "reason": "snapshot-or-summary-not-created",
            "source_topic": "game.actions.v1",
            "summary": None,
        })

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_action = [
        {
            "event_type": row["event_type"],
            "action_label": ACTION_LABELS.get(
                row["event_type"], row["event_type"]
            ),
            "count": row["count"],
        }
        for row in summary["by_action"]
    ]
    return JsonResponse({
        "available": True,
        "source_topic": manifest["topic"],
        "source_kind": "bounded-kafka-snapshot",
        "raw_record_count": manifest["record_count"],
        "bounds": manifest["bounds"],
        "label_source": "current-display-map",
        "summary": {
            "generated_at": summary["generated_at"],
            "event_count": summary["event_count"],
            "by_action": by_action,
            "by_room": summary["by_room"],
        },
    })

@require_GET
def windows_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    path = settings.DATA_DIR / "marts" / "windows.json"
    if not path.exists():
        return JsonResponse({"available": False, "windows": []})
    result = json.loads(path.read_text(encoding="utf-8"))
    return JsonResponse({"available": True, **result})

@login_required
def metrics_snapshot(request):
    path = settings.DATA_DIR / "marts" / "game-metrics.json"
    if not path.exists():
        return JsonResponse({"available": False, "metrics": None})
    report = json.loads(path.read_text(encoding="utf-8"))
    return JsonResponse({"available": True, "metrics": report})


@login_required
def load_snapshot(request):
    path = settings.DATA_DIR / "load" / "run-50.json"
    if not path.exists():
        return JsonResponse({"available": False, "load": None})
    source = json.loads(path.read_text(encoding="utf-8"))
    keys = [
        "generated_at", "measurement_started_at", "profile",
        "connected_success", "connected_peak",
        "attempt_count", "success_count", "error_count",
        "elapsed_seconds", "success_per_second",
        "rtt_sample_count", "rtt_mean_ms", "rtt_p95_ms",
    ]
    report = {key: source[key] for key in keys}
    by_room = {}
    for row in source["by_player"]:
        item = by_room.setdefault(
            row["room_id"], {"connected": 0, "success_count": 0}
        )
        item["connected"] += int(row["connected"])
        item["success_count"] += row["success_count"]
    report["by_room"] = [
        {"room_id": key, **value}
        for key, value in sorted(by_room.items())
    ]
    return JsonResponse({"available": True, "load": report})
