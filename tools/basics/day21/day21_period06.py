# 합치기 전후의 파일별 행을 펼쳐 파일 수와 논리 내용이 보존되는지 비교한다.
before = [["e1"], ["e2"], ["e3"]]
after = [["e1", "e2",], ["e3"]]
old_rows = []
new_rows = []
for part in before:
    old_rows.extend(part)

for part in after:
    new_rows.extend(part)
print("files", len(before), len(after))
print("same", sorted(old_rows) == sorted(new_rows))
