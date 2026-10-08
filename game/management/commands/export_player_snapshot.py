import hashlib
import json
import os
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.utils import timezone

from game.models import Player

class Command(BaseCommand):
    help = "게임 공개 상태를 player-snapshot/v1 NDJSON으로 내보냅니다."

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        target = Path(options["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        captured_at = timezone.now().isoformat()
        # [문제 1 · 한 줄] 실제 Player를 ID 순서로 공개 다섯 필드만 조회한다.
        # 예시: entries = Entry.objects.order_by("code").values("code", "score").iterator()
        rows = Player.objects.order_by("id").values("id", "room_id", "coins", "version", "updated_at").iterator()
        temporary_path = None
        count = 0
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=target.parent, delete=False) as stream:
                temporary_path = Path(stream.name)
                for player in rows:
                    updated_at = player["updated_at"]
                    if timezone.is_naive(updated_at):
                        raise ValueError("updated_at에 시간대가 없습니다.")
                    # [문제 2 · 여러 줄] 공개 상태에 수집 정보를 붙이고 수정 시각을 문자열로 넣는다. (3줄)
                    # 예시: packet = {"schema": "score/v1",
                    #                 "source": "scores", "collected_at": collected_at,
                    #                 **entry, "changed_at": changed_at.isoformat()}
                    row = {"schema_version": "player-snapshot/v1",
                              "source_kind": "player-snapshot", "captured_at": captured_at,
                               **player, "updated_at": updated_at.isoformat()}

                    # [문제 3 · 여러 줄] JSON 한 행을 쓰고 작성한 행 수를 센다. (2줄)
                    # 예시: output.write(json.dumps(packet, ensure_ascii=False, sort_keys=True) + "\n")
                    #       written += 1
                    stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    count += 1

            checksum = hashlib.sha256(temporary_path.read_bytes()).hexdigest()
            # [문제 4 · 한 단어] 완성한 임시 파일을 최종 경로로 교체하는 os 함수다.
            # 힌트 4: 읽기·이동 준비가 끝난 뒤 기존 대상 경로를 바꾼다.
            os.replace(temporary_path, target)
        except (OSError, TypeError, ValueError, DatabaseError) as exc:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise CommandError(str(exc)) from exc
        self.stdout.write(json.dumps({"path": str(target), "rows": count, "sha256": checksum,
                                      "schema_version": "player-snapshot/v1",
                                      "source_kind": "player-snapshot",
                                      "captured_at": captured_at if count else None},
                                     ensure_ascii=False, sort_keys=True))