# 전체 행 수와 set으로 모은 서로 다른 key 수를 비교한다.
rows = [{"partition": 0, "key": "7"}, {"partition": 0, "key": "8"}, {"partition": 3, "key": "7"}]
print("첫 행", rows[0])
print("행 수", len(rows))
keys = set()
for row in rows:
    keys.add(row["key"])
print("서로 다른 key", len(keys))