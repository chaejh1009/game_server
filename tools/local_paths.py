import argparse
import json
from pathlib import Path
from custom_error import InvalidRunIdError

# 실행 ID와 허용 파일 이름을 검증한 뒤 사본의 로컬 경로를 반환한다.
def copy_path(run_id, filename):
    if not run_id.replace("-", "").isalnum():
        raise InvalidRunIdError("run_id is not valid.")
    # 예시: sample_name = "report.json"
    #       if sample_name not in {"report.json", "total.json"}:
    #           raise ValueError("unsupported sample")
    # [문제 1 · 여러 줄] filename이 events.ndjson 또는 manifest.json인지 검사하고, 아니면 ValueError를 발생시켜보세요. (2줄)
    if filename not in ["events.ndjson", "manifest.json"]:
        raise ValueError("unsupported sample")
    # [문제 2 · 한 단어] 사본 기준 경로를 만드는 클래스를 채워보세요.
    # [문제 3 · 한 단어] 기준 경로와 파일 이름 사이에 수집 실행 ID를 넣어보세요.
    return Path("data/copies/bronze/game") / run_id / filename

# 파일을 직접 실행하면 같은 수집본의 두 사본 경로와 배치 버전을 출력한다.
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    # 예시: parser = argparse.ArgumentParser()
    #       options = parser.parse_args()
    # [문제 4 · 한 줄] 명령행 인자를 해석해서 args에 저장하는 한 줄을 작성해보세요.
    args = p.parse_args()
    print(json.dumps({
        "payload_path": copy_path(args.run_id, "events.ndjson").as_posix(),
        "manifest_path": copy_path(args.run_id, "manifest.json").as_posix(),
        "layout_version": "v1",
    }, indent=2))