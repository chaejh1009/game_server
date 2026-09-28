import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from game.models import Player, GameEvent
from game.services import serialize_player
from django.contrib.auth import authenticate, login as auth_login
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie


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

@require_GET
@ensure_csrf_cookie
def csrf_view(request):
    return JsonResponse({
        "csrfToken": get_token(request),
    })


@require_POST
def api_login(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({
            "error": "invalid_json",
        }, status=400)

    username = payload.get("username")
    password = payload.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse({
            "error": "missing_credentials",
        }, status=400)

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse({
            "authenticated": False,
        }, status=401)

    auth_login(request, user)

    return JsonResponse({
        "authenticated": True,
    })
