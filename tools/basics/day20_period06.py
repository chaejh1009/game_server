import json

# 작은 화면 집계를 JSON 문자열로 바꿨다가 다시 사전으로 읽는다.
rows = [{"room_id": "a", "count": 2}, {"room_id": "b", "count": 1}]
summary = {"event_count": 3, "by_room": rows, "dataset_version":"capture-001",}
text = json.dumps(summary, ensure_ascii=False)
print(text)
restored = json.loads(text)
print(restored["event_count"])
print(restored["by_room"][0]["room_id"])