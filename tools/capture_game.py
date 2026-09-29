import argparse
import json
import os
from pathlib import Path
from confluent_kafka import Consumer, TopicPartition
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# 출력 경로를 받고 자동 커밋 없는 수집용 Consumer를 만든다.
p = argparse.ArgumentParser()
p.add_argument("--output", required=True)
args = p.parse_args()
topic = "game.actions.v1"
c = Consumer({
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"],
    "group.id": "village-lake-capture",
    "enable.auto.commit": False,
    "auto.offset.reset": "earliest",
})

# 파티션별 시작·끝 위치를 고정하고 각 low부터 읽도록 배정한다.
# high는 수집에 포함하지 않는 끝의 다음 offset이다.
parts = c.list_topics(topic, timeout=15).topics[topic].partitions
bounds = {}
assignment = []
for part in sorted(parts):
    low, high = c.get_watermark_offsets(TopicPartition(topic, part), timeout=15)
    bounds[part] = [low, high]
    assignment.append(TopicPartition(topic, part, low))
c.assign(assignment)

# 비어 있지 않은 파티션만 수집 대상으로 삼고 임시 파일을 준비한다.
target = Path(args.output)
target.parent.mkdir(parents=True, exist_ok=True)
pending = {part for part, (low, high) in bounds.items() if low < high}
tmp = target.with_suffix(".ndjson.tmp")
count = 0
try:
    with tmp.open("w", encoding="utf-8") as f:
        while pending:
            # 메시지를 기다리되 시간 초과나 Kafka 오류가 발생하면 수집을 중단한다.
            msg = c.poll(10)
            if msg is None:
                raise TimeoutError("bounded capture did not advance")
            if msg.error():
                raise RuntimeError(str(msg.error()))

            # 미완료 파티션에서 고정한 high 미만의 기록을 원문과 전달 위치로 저장한다.
            part = msg.partition()
            if part not in pending:
                continue
            low, high = bounds[part]
            if msg.offset() < high:
                row = {
                    "topic": topic, "partition": part,
                    "offset": msg.offset(),
                    "key": None if msg.key() is None else msg.key().decode(),
                    "value": None if msg.value() is None else msg.value().decode(),
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1

            # 마지막 포함 offset까지 읽은 파티션은 완료 처리한다.
            if msg.offset() >= high - 1:
                pending.remove(part)

    # 모든 파티션을 읽은 뒤에만 최종 파일로 교체한다.
    tmp.replace(target)
finally:
    # 성공·실패와 관계없이 Consumer 연결을 닫는다.
    c.close()
print(json.dumps({"rows": count, "bounds": bounds, "output": str(target)}))