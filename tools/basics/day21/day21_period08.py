# 파일 정리 전후에 화면 행동 수와 방 수가 같은지 비교한다.
before = {"event_count": 3, "rooms": 2}
after = {"event_count": 3, "rooms": 2}
print("event_count", before["event_count"] == after["event_count"])
print("rooms", before["rooms"] == after["rooms"])
print("최종 통과 : ", 
      ((before["event_count"] == after["event_count"]) 
       and 
       (before["rooms"] == after["rooms"])))