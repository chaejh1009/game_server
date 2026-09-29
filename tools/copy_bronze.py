import argparse
import json
from pathlib import Path
from local_paths import copy_path

# 실행 ID를 받고 두 사본 경로를 계산하면서 입력을 먼저 검증한다.
p = argparse.ArgumentParser()
p.add_argument("--run-id", required=True)
args = p.parse_args()
# 예시: sample_path = copy_path("example-001", "events.ndjson")
# [문제 1 · 한 줄] 현재 실행 ID를 검사하고 events.ndjson의 사본 경로를 payload_copy에 저장해보세요.
payload_copy = copy_path(args.run_id, "events.ndjson")
manifest_copy = copy_path(args.run_id, "manifest.json")

# 원본 폴더에서 이벤트와 설명서의 바이트를 모두 읽는다.
source = Path("data/lake/bronze/game") / args.run_id
# 예시: sample = Path("data/practice/copy-demo/source.txt")
#       sample_bytes = sample.read_bytes()
# [문제 2 · 여러 줄] source의 두 파일을 각각 payload_bytes와 manifest_bytes로 읽어보세요. (2줄)
payload_bytes = (source / "events.ndjson").read_bytes()

manifest_bytes = (source / "manifest.json").read_bytes()

# 새 사본 폴더를 만들며 같은 실행 폴더가 이미 있으면 쓰기 전에 중단한다.
# [문제 3 · 한 단어] 이미 있는 사본 폴더를 허용하지 않는 불리언 값을 채워보세요.
payload_copy.parent.mkdir(parents=True, exist_ok=False)

# 이벤트 사본을 먼저 기록하고 같은 수집본의 설명서를 나중에 기록한다.
payload_copy.write_bytes(payload_bytes)
# [문제 4 · 한 단어] 읽어 둔 설명서 바이트를 그대로 기록하는 메서드를 채워보세요.
manifest_copy.write_bytes(manifest_bytes)

# 실제 사본 파일의 이름과 바이트 수를 모아 출력한다.
files = [
    {"name": payload_copy.name, "bytes": len(payload_copy.read_bytes())},
    {"name": manifest_copy.name, "bytes": len(manifest_copy.read_bytes())},
]
print(json.dumps({
    "run_id": args.run_id,
    "directory": payload_copy.parent.as_posix(),
    "files": files,
}, indent=2))

print(len(payload_copy.read_bytes()) + len(manifest_copy.read_bytes()))