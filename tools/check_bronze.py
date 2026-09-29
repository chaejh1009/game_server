import argparse
import hashlib
import json
from pathlib import Path

# 로컬 사본과 같은 수집본의 원본 폴더 manifest 경로를 받는다.
p = argparse.ArgumentParser()
p.add_argument("--data", required=True)
p.add_argument("--manifest", required=True)
args = p.parse_args()

# 실제 bytes에서 길이·지문·빈 줄을 제외한 행 수를 계산한다.
raw = Path(args.data).read_bytes()
# 예시: settings = json.loads(Path("settings.json").read_text(encoding="utf-8"))
# [문제 1 · 한 줄] 원본 폴더 manifest 파일의 UTF-8 텍스트를 읽고 JSON 사전으로 해석해보세요.
manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

# 예시: sample = {
#           "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(),
#       }
# [문제 2 · 여러 줄] raw의 길이·SHA-256·빈 줄을 뺀 행 수를 observed 사전으로 작성해보세요. (5줄)
observed = {
    "bytes": len(raw), 
    "sha256": hashlib.sha256(raw).hexdigest(),
    "rows": len(raw.splitlines()),
}

# manifest의 세 기준과 비교하고 하나라도 다르면 실패로 종료한다.
# [문제 3 · 한 단어] 빈칸을 채워보세요.
checks = {key: observed[key] == manifest[key] for key in observed}

print(json.dumps({"observed": observed, "checks": checks}, indent=2))
# [문제 4 · 한 단어] 빈칸을 채워보세요.
if not all(checks.values()):
    raise SystemExit("copy does not match manifest")