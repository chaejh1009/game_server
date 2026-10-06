# 같은 여덟 행을 두 파일과 네 파일에 나눈 구성을 비교한다.
profiles = {"tasks-2": [4, 4], "tasks-4": [2, 2, 2, 2], "tasks-5":[2, 2, 2, 1, 1]}
for name, files in profiles.items():
    print(name, "files", len(files), "rows", sum(files))