from __future__ import annotations
from enum import Enum, auto
import pickle

class State(Enum):
    WAITING = auto()
    GAME = auto()
    EXIT = auto()

class MsgType(Enum):
    ID = auto()
    GAMESTART = auto()
    EXIT = auto()
    SURFACE = auto()

class Msg:
    def __init__(self, typ, data):
        self.type = typ
        self.data = data

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data) -> Msg:
        return pickle.loads(data)

    def __str__(self):
        return f"{self.type}: {self.data}"