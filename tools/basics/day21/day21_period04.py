# 목표 날짜와 같은 행만 모아 선택 날짜와 건수를 확인한다.
rows = [{"date": "2026-09-11", "event_id": "e1"}, {"date": "2026-09-12", "event_id": "e2"}]
target = "2026-09-11"
selected = []
for row in rows:
    if row["date"] == target:
        selected.append(row)
print("날짜", target)
print("행 수", len(selected))