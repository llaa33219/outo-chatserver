import time
from collections import defaultdict


TTL_SECONDS = 5


class TypingManager:
    def __init__(self):
        self._state: dict[str, dict[str, tuple[str, float]]] = defaultdict(dict)

    def set_typing(self, room_id: str, user_id: str, username: str, is_typing: bool):
        if is_typing:
            self._state[room_id][user_id] = (username, time.monotonic())
        else:
            self._state[room_id].pop(user_id, None)

    def get_typing_users(self, room_id: str) -> list[dict]:
        now = time.monotonic()
        expired = [
            uid
            for uid, (_, ts) in self._state[room_id].items()
            if now - ts > TTL_SECONDS
        ]
        for uid in expired:
            del self._state[room_id][uid]

        return [
            {"user_id": uid, "username": uname}
            for uid, (uname, _) in self._state[room_id].items()
        ]


typing_manager = TypingManager()
