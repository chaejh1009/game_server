# 방 ID를 키로 삼아 각 행을 해당 방의 누계에 더한다.
rows = [{"room_id": "a"}, {"room_id": "a"}, {"room_id": "b"}]
counts = {}
for row in rows:
    room = row["room_id"]
    counts[room] = counts.get(room, 0) + 1
print(counts)

print(sum(counts.values()))