# 세 멤버의 주소·역할과 전체 멤버 수를 읽는다.
members = [{"name": "local-1", "state": "PRIMARY"}, {"name": "local-2", "state": "SECONDARY"}, {"name": "local-3", "state": "SECONDARY"}]
for member in members:
    print(member["name"], member["state"])
print("members", len(members))