from dataclasses import dataclass


@dataclass
class GameEvent:
    read: bool
    time_stamp: float
    health: int
    food: int
    environment: str
