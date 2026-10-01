# 같은 입력 bytes를 두 압축 이름과 함께 출력한다. 실제 압축은 아직 수행하지 않는다.
data = b'game-event\n' * 4
profiles = ["snappy", "zstd"]
profiles.reverse()
for codec in profiles:
    print(codec, "input_bytes", len(data))