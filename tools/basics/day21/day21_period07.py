# 전체 bytes를 파일 수로 나눠 평균 파일 크기를 확인한다.
report = {"bytes": 120, "files": 3, "rows": 8}
average = 0
if report["files"]:
    average = report["bytes"] / report["files"]

print("average_bytes", average)
print("rows", report["rows"])