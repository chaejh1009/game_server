from datetime import datetime, timedelta, timezone

# 같은 시각을 UTC와 한국 시간으로 표시해 날짜가 바뀌는 경계를 확인한다.
utc = datetime.fromisoformat("2026-09-11T00:00:00+00:00")
korea = utc.astimezone(timezone(timedelta(hours=9)))
print("UTC", utc.date())
print("한국", korea.date())