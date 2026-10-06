# event_id 유무를 기준으로 정상 행과 보류 행을 나눈 뒤 각각 센다.
rows = [{"event_id": "e1", "room_id": "a"}, {"event_id": None, "room_id": "a"}]
accepted = []
held = []
for row in rows:
    if row["event_id"] is not None:
        accepted.append(row)
    else:
        held.append(row)
print("accepted", len(accepted))
print("held", len(held))
print((len(accepted) + len(held)) == len(rows))