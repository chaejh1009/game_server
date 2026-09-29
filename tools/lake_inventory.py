import json
from pathlib import Path

# 전일 화면 집계 파일을 읽어 현재 저장 현황의 입력으로 삼는다.
root = Path("data")
summary_path = ".." / root / "marts" / "game-summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))

# 집계 위치·원본의 두 식별자·현재 상태의 기준 저장소를 구분해 기록한다.
# rebuildable은 원본을 보존할 때만 성립한다.
result = {
    "schema_version": 1,
    "serving": {
        "path": str(summary_path),
        "event_count": summary["event_count"],
        "rebuildable": True,
    },
    "source": {
        "topic": "game.actions.v1",
        "identity": "event_id",
        "position": ["topic", "partition", "offset"],
        "purpose": "rebuild daily statistics",
    },
    "state_owner": "MySQL game_player",
}

# 현황을 UTF-8 JSON 파일로 저장하고 같은 내용을 출력한다.
out = ".." / root / "contracts" / "lake-inventory.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))