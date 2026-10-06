# 수집 실행 ID와 지문을 계약에 복사하고 원본 참조와 일치하는지 확인한다.
source = {"run_id": "capture-002", "sha256": "demo-fingerprint"}
contract = {"schema_version": 1, "source": dict(source)}
print(contract["source"]["run_id"])
print("matched", source["sha256"] == contract["source"]["sha256"])