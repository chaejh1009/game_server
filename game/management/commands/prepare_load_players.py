import getpass
import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from game.models import Player


class Command(BaseCommand):
    help = "Create classroom load users without replacing existing passwords."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20)
        parser.add_argument("--prefix", default="day18_")
        parser.add_argument("--rooms", default="load18")
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        count = options["count"]
        prefix = options["prefix"]
        room_prefix = options["rooms"]
        if not 1 <= count <= 200:
            raise CommandError("--count must be between 1 and 200.")
        if not prefix or not room_prefix:
            raise CommandError("Use a non-empty prefix and room prefix.")
        password = getpass.getpass("Classroom load-user password: ")
        if not password:
            raise CommandError("A password is required.")
        User = get_user_model()
        rows = []
        created_count = 0

        with transaction.atomic():
            for number in range(1, count + 1):
                username = f"{prefix}{number:03d}"
                room_number = (number - 1) // 20 + 1
                room_id = f"{room_prefix}-{room_number:02d}"
                user, user_created = User.objects.get_or_create(
                    username=username,
                )
                if user_created:
                    user.set_password(password)
                    user.save(update_fields=["password"])
                    created_count += 1
                elif not user.check_password(password):
                    raise CommandError(
                        f"{username} exists with a different password."
                    )

                player = Player.objects.filter(user=user).first()
                if player is None:
                    room_size = Player.objects.filter(
                        room_id=room_id,
                    ).count()
                    if room_size >= 20:
                        raise CommandError(f"{room_id} already has 20 players.")
                    player = Player.objects.create(
                        user=user, room_id=room_id,
                        x=1, y=1, coins=0, version=0,
                    )
                elif player.room_id != room_id:
                    raise CommandError(
                        f"{username} is assigned to another room."
                    )
                rows.append({
                    "username": username,
                    "room_id": player.room_id,
                    "player_id": player.pk,
                })

        output = Path(options["output"]).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(
                {"schema_version": 1, "accounts": rows},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )
        temporary.replace(output)
        self.stdout.write(
            f"accounts={len(rows)} new_users={created_count} output={output}"
        )