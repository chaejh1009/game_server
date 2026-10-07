import json
from functools import wraps
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from django.conf import settings
from django.http import JsonResponse
from .models import Player
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

# 로그인한 게임 유저의 공개 식별자와 허용된 상태만 매체 payload로 만든다.
def media_payload(user):
    player = Player.objects.get(user=user)
    return {
        "subject": {"media_id": settings.ADS_MEDIA_ID, "subject_id": str(player.pk)},
        "context": {
            "player_id": str(player.pk), "room_id": player.room_id,
            "coins": player.coins, "version": player.version,
            "context_source": "mysql-live-v1",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        },
    }


# 키는 서버에서만 붙인다. 광고 서버 호출에 게임 쿠키·비밀번호를 전달하지 않는다.
def call_ads(path, payload):
    request = Request(
        settings.ADS_BASE_URL.rstrip("/") + path,
        data=json.dumps(payload, allow_nan=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Media-ID": settings.ADS_MEDIA_ID,
            "X-Media-Key": settings.ADS_MEDIA_KEY
            },
        method="POST",
    )
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        try:
            body = json.loads(exc.read(65536))
            error = body.get("error", "") if isinstance(body, dict) else ""
            code = error.split(":", 1)[0] if isinstance(error, str) else ""
            if code in {"decision_snapshot_missing", "decision_not_found_for_subject",
                        "impression_required", "decision_id_required", "event_type_invalid"}:
                return exc.code, {"error": code}
        except (ValueError, UnicodeDecodeError, OSError):
            pass
        return exc.code, {"error": "ad_request_rejected"}
    except (URLError, TimeoutError, ValueError):
        return 503, {"error": "ads_unavailable"}


# 게임 쿠키 인증·CSRF를 유지하고 광고 장애는 광고 JSON 응답으로만 표현한다.
def viewer_methods(*allowed):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "login_required"}, status=401)
            if request.method not in allowed:
                response = JsonResponse({"error": "method_not_allowed"}, status=405)
                response["Allow"] = ", ".join(allowed)
                return response
            try:
                return view(request, *args, **kwargs)
            except Player.DoesNotExist:
                return JsonResponse({"error": "player_required"}, status=409)
            except (ValueError, UnicodeDecodeError):
                return JsonResponse({"error": "invalid_ad_request"}, status=400)
        return wrapped
    return decorate


@viewer_methods("GET")
def decision(request):
    payload = media_payload(request.user)
    payload["slot_id"] = request.GET.get("slot_id")
    status, result = call_ads("/api/media/decision/", payload)
    response = JsonResponse(result, status=status)
    response["Cache-Control"] = "no-store"
    return response

class AdsUnavailable(Exception):
    pass


def request_decision(player, slot_id):
    media_id = settings.ADS_MEDIA_ID
    if not settings.ADS_MEDIA_KEY:
        raise AdsUnavailable("media_key_missing")

    payload = {
        "media_id": media_id,
        "subject": {
            "media_id": media_id,
            "subject_id": str(player.pk),
        },
        "slot_id": slot_id,
        "context": {},
    }
    request = Request(
        settings.ADS_BASE_URL.rstrip("/") + "/api/media/decision/",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Media-ID": media_id,
            "X-Media-Key": settings.ADS_MEDIA_KEY,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=3) as response:
            data = json.load(response)

        if not isinstance(data, dict):
            raise ValueError("invalid_response")

        # 현재 광고 서버의 빈 광고 응답을 처리한다.
        if data.get("empty") is True or data.get("ad", "selected") is None:
            return {**data, "ad": None}

        if data.get("slot_id") != slot_id:
            raise ValueError("slot_mismatch")

        # 이미지 경로와 기존 필드를 보존하고 확인 화면용 필드를 추가한다.
        return {
            **data,
            "body": data.get("body", ""),
            "bid_amount": data.get("bid_amount", data.get("bid_units")),
        }

    except (
        HTTPError, URLError, TimeoutError, OSError,
        ValueError, KeyError, TypeError,
    ) as error:
        raise AdsUnavailable("ads_unavailable") from error

def request_ad_event(player, decision_id, event_type):
    """Use the logged-in player's identity; clients supply only the event target."""
    if not settings.ADS_MEDIA_KEY:
        raise AdsUnavailable("media_key_missing")
    if (not isinstance(decision_id, str) or not decision_id
            or len(decision_id) > 128 or event_type not in ("impression", "click")):
        raise ValueError("invalid_ad_event")
    # [문제 1 · 여러 줄] 매체·로그인 Player·결정·종류를 payload에 구성한다. (9줄)
    # 예시: packet = {"device": {"id": str(device.pk)}, "action": action}
    payload = {
        "media_id": settings.ADS_MEDIA_ID,
        "subject": {
            "media_id": settings.ADS_MEDIA_ID,
            "subject_id": str(player.pk),
        },
        "decision_id": decision_id,
        "event_type": event_type,
    }

    # [문제 2 · 한 줄] events API를 호출하고 두 반환값을 status, data로 받는다.
    # 예시: status, data = send_message("/api/messages/", packet)
    status, data = call_ads("/api/media/events/", payload)

    if status == 503:
        raise AdsUnavailable("ads_unavailable")
    # [문제 3 · 여러 줄] 거절 응답과 잘못된 성공 응답을 구별한다. (10줄)
    # 예시: if status != 200:
    #           raise ValueError("message_rejected")
    #       if not isinstance(data, dict) or data.get("id") != message_id:
    #           raise ServiceUnavailable("invalid_response")

    if status != 200:
        code = data.get("error") if isinstance(data, dict) else None
        allowed = {"decision_snapshot_missing", "decision_not_found_for_subject",
                "impression_required", "decision_id_required", "event_type_invalid"}
        raise ValueError(code if code in allowed else "ad_event_rejected")
    if (not isinstance(data, dict)
            or data.get("event_id") != decision_id + ":" + event_type
            or data.get("event_type") != event_type
            or type(data.get("created")) is not bool):
        raise AdsUnavailable("invalid_ad_event_response")

    return {name: data[name] for name in ("event_id", "event_type", "created")}