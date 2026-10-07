"""Authenticated game-to-media event bridge with the existing game CSRF policy."""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from game.ad_gateway import AdsUnavailable, request_ad_event
from game.models import Player


@require_POST
def ad_event(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    player = Player.objects.filter(user=request.user).first()
    if player is None:
        return JsonResponse({"error": "player_missing"}, status=409)
    try:
        body = json.loads(request.body)
        if (not isinstance(body, dict)
                or set(body) != {"decision_id", "event_type"}):
            raise ValueError("invalid_ad_event")
        data = request_ad_event(player, body["decision_id"], body["event_type"])
        response = JsonResponse(data)
        response["Cache-Control"] = "no-store"
        return response
    except (ValueError, UnicodeDecodeError) as error:
        code = str(error)
        allowed = {"decision_snapshot_missing", "decision_not_found_for_subject",
                   "impression_required", "decision_id_required", "event_type_invalid"}
        return JsonResponse({"error": code if code in allowed else "ad_event_rejected"}, status=400)
    except AdsUnavailable:
        return JsonResponse({"error": "ads_unavailable"}, status=503)