import time
from dataclasses import dataclass
from math import floor


def create_game_event(bot, env: str):
    if bot:
        return GameEvent(time_stamp=time.time(), health=floor(bot.health), food=bot.food, environment=env, read=False)
    else:
        return None


@dataclass
class GameEvent:
    read: bool
    time_stamp: float
    health: int
    food: int
    environment: str | None
