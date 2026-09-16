import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from kafka import KafkaConsumer, TopicPartition


class Command(BaseCommand):
    help = "Read offsets without consuming or committing game events."

    def add_arguments(self, parser):
        parser.add_argument("--topic", default="game.events.v1")
        parser.add_argument("--group", default="day13-analysis-a")

    def handle(self, *args, **options):
        # Kafka Consumer 객체를 생성합니다.
        consumer = KafkaConsumer(

            # 접속할 Kafka Broker 주소 목록을 Django settings에서 가져옵니다.
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,

            # 이 Consumer가 속할 Consumer Group ID를 커맨드 옵션에서 가져옵니다.
            group_id=options["group"],

            # 메시지를 읽었다고 해서 offset을 자동으로 commit하지 않도록 설정합니다.
            enable_auto_commit=False,

            # Kafka Broker의 응답을 최대 15초까지 기다립니다.
            request_timeout_ms=15000,
        )

        # 이후 파티션별 조회 결과를 저장하기 위한 빈 리스트입니다.
        rows = []

        # Kafka 조회 과정에서 발생할 수 있는 예외를 처리하기 위해 try 블록을 시작합니다.
        try:

            # 실행 옵션으로 전달받은 Kafka Topic 이름을 가져옵니다.
            topic = options["topic"]

            # 해당 Topic에 존재하는 Partition 번호들을 Kafka에 조회합니다.
            # 예: {0, 1, 2}
            numbers = consumer.partitions_for_topic(topic)

            # Topic의 Partition 정보를 가져오지 못했는지 확인합니다.
            if numbers is None:

                # Partition 정보를 조회하지 못했다면 Django CommandError를 발생시킵니다.
                raise CommandError("Topic metadata is unavailable.")

            # Partition 번호들을 실제 Kafka TopicPartition 객체로 변환합니다.
            partitions = [

                # Topic 이름과 Partition 번호를 묶어서 특정 Partition을 표현합니다.
                # 예: TopicPartition("game.events.v1", 0)
                TopicPartition(topic, number) 

                # Partition 번호들을 정렬한 뒤 하나씩 반복합니다.
                # 예: {2, 0, 1} → [0, 1, 2]
                for number in sorted(numbers)
            ]

            # 각 Partition에서 현재 Kafka가 보관하고 있는
            # 가장 오래된 메시지의 offset을 조회합니다.
            beginnings = consumer.beginning_offsets(partitions)

            # 각 Partition의 마지막 메시지 "다음 위치" offset을 조회합니다.
            # 예: 마지막 메시지 offset이 99라면 end offset은 100입니다.
            ends = consumer.end_offsets(partitions)
            # partitions 리스트에 들어있는 TopicPartition 객체를 하나씩 꺼냅니다.
            for tp in partitions:

                # 현재 Consumer Group이 이 Partition에서 마지막으로 commit한 offset을 조회합니다.
                # 한 번도 commit한 적이 없다면 None이 반환될 수 있습니다.
                saved = consumer.committed(tp)

                # 현재 Partition의 상태를 딕셔너리 형태로 rows 리스트에 추가합니다.
                rows.append({

                    # 현재 Partition이 속한 Topic 이름을 저장합니다.
                    # 예: "game.events.v1"
                    "topic": tp.topic,

                    # 현재 Partition 번호를 저장합니다.
                    # 예: 0, 1, 2
                    "partition": tp.partition,

                    # 현재 Kafka가 이 Partition에서 보관하고 있는
                    # 가장 오래된 메시지의 offset을 저장합니다.
                    "beginning_offset": beginnings[tp],

                    # 현재 Partition의 마지막 메시지 다음 위치의 offset을 저장합니다.
                    # 예: 마지막 메시지가 99번이면 end_offset은 100입니다.
                    "end_offset": ends[tp],

                    # 현재 Consumer Group이 이 Partition에서
                    # 마지막으로 commit한 offset을 저장합니다.
                    "committed_offset": saved,

                    # commit된 offset이 실제로 존재하는지 True/False로 저장합니다.
                    # saved가 None이 아니면 True, None이면 False입니다.
                    "has_committed_offset": saved is not None,
                })

        # try 블록에서 예외가 발생하든 정상 종료되든
        # 반드시 실행되는 영역입니다.
        finally:

            # Kafka Consumer 연결을 종료합니다.
            # autocommit=False이므로 close할 때도 offset을 자동 commit하지 않습니다.
            consumer.close(autocommit=False)

            # Django management command의 표준 출력(stdout)으로 결과를 출력합니다.
            self.stdout.write(

                # Python 딕셔너리를 JSON 문자열로 변환합니다.
                json.dumps({

                    # 실행할 때 전달받은 Consumer Group ID를 결과에 포함합니다.
                    "group_id": options["group"],

                    # 위 반복문에서 만든 Partition별 상태 목록을 결과에 포함합니다.
                    "partitions": rows,

                # 한글 등의 유니코드 문자를 \uXXXX 형태로 변환하지 않고 그대로 출력합니다.
                }, ensure_ascii=False,

                # JSON을 보기 좋게 2칸 들여쓰기 형식으로 출력합니다.
                indent=2))