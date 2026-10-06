# 전달 기록 수와 event_id 중복을 제외한 논리 행동 수를 비교한다.
rows = [{"event_id": "e1", "offset": 10}, {"event_id": "e1", "offset": 11}, {"event_id": "e2", "offset": 12}]
ids = set()
for row in rows:
    ids.add(row["event_id"])
print("accepted", len(rows))
print("logical", len(ids))
# 중복 전달된 요소 개수 체크
duplicate_deliveries = len(rows) - len(ids)
print("duplicate_deliveries : ",  duplicate_deliveries)