# 끝의 다음 위치인 high는 제외하고 그보다 작은 offset만 모은다.
offsets = [100, 101, 102, 103]
high = 104
captured = []
for offset in offsets:
    if offset < high:
        captured.append(offset)
print("끝의 다음 위치", high)
print("포함", captured)