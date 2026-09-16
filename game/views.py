from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from game.models import Player, GameEvent
from game.services import serialize_player

@require_GET
def player_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    player = Player.objects.get(user=request.user)
    return JsonResponse(serialize_player(player))

@login_required
def play(request):
    return render(request, "game/play.html")

@require_GET
def delivery_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    events = GameEvent.objects.filter(player__user=request.user)
    return JsonResponse({
        "source": "mysql-outbox",
        "event_count": events.count(),
        "pending_publish_count": events.filter(published_at__isnull=True).count(),
    })

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from game.models import GameEvent
from game.services import serialize_event


@login_required
def history(request):
    events = GameEvent.objects.filter(
        player__user=request.user
    ).order_by("-event_time", "-event_id")[:20]
    return JsonResponse({
        "scope": "current-player",
        "limit": 20,
        "events": [serialize_event(event) for event in events],
    })