import json

# JSON으로 직렬화했다가 읽어 행 수와 논리 내용이 같은지 확인한다.
rows = [{"event_id": "e1", "room_id": "a"}]
print("직렬화 전 : ", len(rows[0]))
text = json.dumps(rows)
restored = json.loads(text)

print("행 수", len(restored[0]))
print("논리 내용 같음", restored == rows)