# 원본에서 필요한 두 열을 새 사전에 담고 원본 열 수와 비교한다.
row = {"event_id": "e1", "player_id": "7", "room_id": "a", "payload": {"coins": 9}}
selected = {"event_id": row["event_id"], "room_id": row["room_id"], "player_id": row["player_id"]}
print(list(selected))
print("원본 열 수", len(row))