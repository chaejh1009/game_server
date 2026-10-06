from pathlib import Path

# 사본의 기준 폴더에 수집 실행 ID와 파일 이름을 이어 경로를 만든다.
base = Path("data/copies/bronze/game")
run_id = "team-a-001"
target = base / run_id / "events.ndjson"
print(target.as_posix())
target2 = base / run_id / "manifest.json"
print(target2.as_posix())
print("run", run_id)