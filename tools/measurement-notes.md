Django: server/ 에서 Daphne 단일 프로세스
게임 상태: MySQL village DB
이벤트 발행: 별도 publisher 한 개
Kafka: 앞선 3 Broker
Spark: 앞선 Master 1 + Worker 2
측정: tools/ws_load.py 를 실행하는 Python 프로세스
표시: python client/main.py 로 실행한 Pygame 창
---
{
  "profile": {
    "clients": 20,
    "seconds": 30,
    "interval_seconds": 1.0,
    "players_per_room": 20,
    "asgi_processes": 1
  },
  "result_fields": [
    "connected_success",
    "connected_peak",
    "attempt_count",
    "success_count",
    "error_count",
    "elapsed_seconds",
    "success_per_second",
    "rtt_mean_ms",
    "rtt_p95_ms"
  ]
}

보고서 파일: data/load/run-20.json
ASGI 프로세스 수: 1
방당 플레이어: 20
서버/측정 도구의 장비 배치: 직접 작성
동시에 실행한 분석 작업: 직접 작성
측정 중 CPU 관찰 도구·대상 프로세스·시점: 직접 작성
{
  "schema_version": 1,
  "generated_at": "2026-09-28T06:11:14.793960+00:00",
  "measurement_started_at": "2026-09-28T06:10:44.788324+00:00",
  "profile": {
    "clients": 20,
    "seconds": 30,
    "interval_seconds": 1.0,
    "players_per_room": 20,
    "asgi_processes": 1,
    "ramp_interval_seconds": 0.1,
    "model": "one-outstanding-command-per-player"
  },
  "environment": {
    "python": "3.12.10",
    "platform": "macOS-26.5.2-arm64-arm-64bit",
    "target": "http://127.0.0.1:8000",
    "server_cpu_note": null
  },
  "connected_success": 20,
  "connected_peak": 20,
  "attempt_count": 580,
  "success_count": 580,
  "error_count": 0,
  "elapsed_seconds": 30.005281375000777,
  "success_per_second": 19.329930379630873,
  "rtt_sample_count": 580,
  "rtt_mean_ms": 251.02761707238923,
  "rtt_p95_ms": 480.8175409998512,
  "by_player": [
    {
      "username": "day18_001",
      "room_id": "load18-01",
      "player_id": 8,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_002",
      "room_id": "load18-01",
      "player_id": 9,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_003",
      "room_id": "load18-01",
      "player_id": 10,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_004",
      "room_id": "load18-01",
      "player_id": 11,
      "connected": true,
      "attempt_count": 28,
      "success_count": 28,
      "errors": []
    },
    {
      "username": "day18_005",
      "room_id": "load18-01",
      "player_id": 12,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_006",
      "room_id": "load18-01",
      "player_id": 13,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_007",
      "room_id": "load18-01",
      "player_id": 14,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_008",
      "room_id": "load18-01",
      "player_id": 15,
      "connected": true,
      "attempt_count": 28,
      "success_count": 28,
      "errors": []
    },
    {
      "username": "day18_009",
      "room_id": "load18-01",
      "player_id": 16,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_010",
      "room_id": "load18-01",
      "player_id": 17,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_011",
      "room_id": "load18-01",
      "player_id": 18,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_012",
      "room_id": "load18-01",
      "player_id": 19,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_013",
      "room_id": "load18-01",
      "player_id": 20,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_014",
      "room_id": "load18-01",
      "player_id": 21,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_015",
      "room_id": "load18-01",
      "player_id": 22,
      "connected": true,
      "attempt_count": 30,
      "success_count": 30,
      "errors": []
    },
    {
      "username": "day18_016",
      "room_id": "load18-01",
      "player_id": 23,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_017",
      "room_id": "load18-01",
      "player_id": 24,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_018",
      "room_id": "load18-01",
      "player_id": 25,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_019",
      "room_id": "load18-01",
      "player_id": 26,
      "connected": true,
      "attempt_count": 29,
      "success_count": 29,
      "errors": []
    },
    {
      "username": "day18_020",
      "room_id": "load18-01",
      "player_id": 27,
      "connected": true,
      "attempt_count": 30,
      "success_count": 30,
      "errors": []
    }
  ]
}