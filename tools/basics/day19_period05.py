from pathlib import Path

# 연습 폴더에 고정된 여섯 바이트 파일을 만든다.
folder = Path("data/practice/copy-demo")
folder.mkdir(parents=True, exist_ok=True)
source = folder / "source.txt"
source.write_bytes(b"hello\n")

# 읽은 바이트를 사본에 쓰고 두 파일의 이름·크기를 출력한다.
copied = folder / "copy.txt"
copied.write_bytes(source.read_bytes())
files = [
    {"name": source.name, "bytes": len(source.read_bytes())},
    {"name": copied.name, "bytes": len(copied.read_bytes())},
]

total_bytes = 0
for item in files:
    print(item["name"], item["bytes"])
    total_bytes += item["bytes"]
print("files", len(files))
print("총 바이트 합  : ", total_bytes)