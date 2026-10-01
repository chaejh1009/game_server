# 채집 이벤트만 선택한 뒤 전체 행 수와 선택한 행 수를 비교한다.
events = [{"event_type": "player.gathered"}, {"event_type": "player.moved"}, {"event_type": "player.gathered"}]
selected = []
for event in events:
    if event["event_type"] == "player.gathered":
        selected.append(event)
print("전체", len(events))
print("채집", len(selected))