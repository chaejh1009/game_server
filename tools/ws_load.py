import argparse
import asyncio
import getpass
import json
import math
import platform
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import aiohttp

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def nearest_rank(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = math.ceil(len(ordered) * fraction) - 1
    return ordered[max(0, index)]

async def csrf_token(session, base_url):
    async with session.get(
        base_url + "/api/auth/csrf/", allow_redirects=False,
    ) as response:
        if response.status != 200:
            raise ValueError("csrf_not_available")
        data = await response.json()
    token = data.get("csrfToken")
    if not isinstance(token, str) or not token:
        raise ValueError("csrf_token_missing")
    return token


async def login(session, base_url, username, password):
    token = await csrf_token(session, base_url)
    async with session.post(
        base_url + "/api/auth/login/",
        json={"username": username, "password": password},
        headers={"X-CSRFToken": token, "Origin": base_url},
        allow_redirects=False,
    ) as response:
        if response.status != 200:
            raise ValueError("login_not_accepted")
        data = await response.json()
        if data.get("authenticated") is not True:
            raise ValueError("login_not_authenticated")

    session.headers["X-CSRFToken"] = await csrf_token(session, base_url)
    session.headers["Origin"] = base_url
    async with session.get(
        base_url + "/api/player/", allow_redirects=False,
    ) as response:
        if response.status != 200:
            raise ValueError("player_not_available")
        state = await response.json()
    return state


async def read_until(socket, condition, timeout_seconds):
    deadline = time.perf_counter() + timeout_seconds
    while True:
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            raise TimeoutError("matching_message_timeout")
        message = await socket.receive(timeout=remaining)
        if message.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(message.data)
            if condition(data):
                return data
        elif message.type in (
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.ERROR,
        ):
            raise ConnectionError("websocket_closed")

async def run_player(account, password, options, gate, ready, shared):
    report = {
        "username": account["username"],
        "room_id": account["room_id"],
        "player_id": account["player_id"],
        "connected": False,
        "attempt_count": 0,
        "success_count": 0,
        "rtt_ms": [],
        "errors": [],
    }
    announced = False
    counted_open = False
    timeout = aiohttp.ClientTimeout(total=15)
    jar = aiohttp.CookieJar(unsafe=True)
    try:
        async with aiohttp.ClientSession(
            cookie_jar=jar, timeout=timeout,
        ) as session:
            state = await login(
                session, options.base_url,
                account["username"], password,
            )
            ws_url = options.base_url.replace("http://", "ws://", 1)
            async with session.ws_connect(
                ws_url + "/ws/play/",
                headers={"Origin": options.base_url},
                heartbeat=20,
            ) as socket:
                await read_until(
                    socket,
                    lambda row: row.get("type") == "snapshot",
                    10,
                )
                report["connected"] = True
                shared["open"] += 1
                counted_open = True
                shared["peak"] = max(shared["peak"], shared["open"])
                ready.put_nowait(True)
                announced = True
                await gate.wait()
                deadline = time.perf_counter() + options.seconds
                while time.perf_counter() < deadline:
                    x = int(state["x"])
                    direction = "right" if x < 10 else "left"
                    command_id = str(uuid.uuid4())
                    started = time.perf_counter()
                    await socket.send_json({
                        "type": "move",
                        "command_id": command_id,
                        "direction": direction,
                    })
                    report["attempt_count"] += 1
                    reply = await read_until(
                        socket,
                        lambda row: row.get("command_id") == command_id
                        and row.get("type") in ("state", "error"),
                        5,
                    )
                    if reply["type"] != "state":
                        report["errors"].append(
                            {"kind": "server_error", "code": reply.get("code")}
                        )
                        break
                    elapsed = time.perf_counter() - started
                    report["success_count"] += 1
                    report["rtt_ms"].append(elapsed * 1000)
                    state = reply
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        break
                    wait_seconds = max(0, options.interval - elapsed)
                    await asyncio.sleep(min(wait_seconds, remaining))
    except (aiohttp.ClientError, TimeoutError, ConnectionError, ValueError) as exc:
        report["errors"].append({
            "kind": type(exc).__name__,
            "message": str(exc)[:120],
        })
    finally:
        if not announced:
            ready.put_nowait(False)
        if counted_open:
            shared["open"] -= 1
    return report

async def run_load(accounts, password, options):
    gate = asyncio.Event()
    ready = asyncio.Queue()
    shared = {"open": 0, "peak": 0}
    tasks = []
    for account in accounts:
        tasks.append(asyncio.create_task(
            run_player(account, password, options, gate, ready, shared)
        ))
        await asyncio.sleep(0.1)

    readiness = [await ready.get() for _ in tasks]
    measurement_started_at = utc_now()
    started = time.perf_counter()
    gate.set()
    reports = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - started
    latencies = [
        value for report in reports for value in report["rtt_ms"]
    ]
    attempts = sum(row["attempt_count"] for row in reports)
    successes = sum(row["success_count"] for row in reports)
    errors = sum(len(row["errors"]) for row in reports)
    public_reports = [
        {key: value for key, value in row.items() if key != "rtt_ms"}
        for row in reports
    ]
    result = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "measurement_started_at": measurement_started_at,
        "profile": {
            "clients": len(accounts),
            "seconds": options.seconds,
            "interval_seconds": options.interval,
            "players_per_room": 20,
            "asgi_processes": 1,
            "ramp_interval_seconds": 0.1,
            "model": "one-outstanding-command-per-player",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "target": options.base_url,
            "server_cpu_note": None,
        },
        "connected_success": sum(readiness),
        "connected_peak": shared["peak"],
        "attempt_count": attempts,
        "success_count": successes,
        "error_count": errors,
        "elapsed_seconds": elapsed,
        "success_per_second": successes / elapsed if elapsed else 0,
        "rtt_sample_count": len(latencies),
        "rtt_mean_ms": sum(latencies) / len(latencies) if latencies else None,
        "rtt_p95_ms": nearest_rank(latencies, 0.95),
        "by_player": public_reports,
    }
    output = Path(options.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    temporary.replace(output)
    print(json.dumps({
        key: result[key] for key in (
            "connected_success", "connected_peak", "attempt_count",
            "success_count", "error_count", "elapsed_seconds",
            "success_per_second", "rtt_mean_ms", "rtt_p95_ms",
        )
    }, ensure_ascii=False, indent=2))
    print("saved:", output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", required=True)
    parser.add_argument("--clients", type=int, default=2)
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", required=True)
    options = parser.parse_args()
    options.base_url = options.base_url.rstrip("/")
    address = urlsplit(options.base_url)
    if (
        address.scheme != "http"
        or address.hostname not in ("127.0.0.1", "localhost")
        or address.path
        or address.query
        or address.fragment
    ):
        parser.error("This classroom tool accepts a local HTTP origin only.")
    if not 1 <= options.clients <= 200:
        parser.error("--clients must be 1..200.")
    if not 5 <= options.seconds <= 120:
        parser.error("--seconds must be 5..120.")
    if options.interval < 0.5:
        parser.error("--interval must be at least 0.5 seconds.")
    value = json.loads(Path(options.accounts).read_text(encoding="utf-8"))
    accounts = value["accounts"][:options.clients]
    if len(accounts) != options.clients:
        parser.error("Prepare enough accounts before this run.")
    if len({row["username"] for row in accounts}) != len(accounts):
        parser.error("Use one unique username per connection.")
    password = getpass.getpass("Classroom load-user password: ")
    asyncio.run(run_load(accounts, password, options))


if __name__ == "__main__":
    main()