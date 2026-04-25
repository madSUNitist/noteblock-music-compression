from typing import Union, Tuple

Vector = Tuple[int, int]  # (dt, dp)

class Point:
    __slots__ = ('tick', 'key', 'instrument')

    def __init__(self, tick: int, key: int, instrument: int):
        self.tick = tick
        self.key = key
        self.instrument = instrument

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return (self.tick == other.tick and
                self.key == other.key and
                self.instrument == other.instrument)

    def __hash__(self):
        return hash((self.tick, self.key, self.instrument))

    def __lt__(self, other):
        if self.tick != other.tick:
            return self.tick < other.tick
        if self.key != other.key:
            return self.key < other.key
            
        return self.instrument < other.instrument

    def __add__(self, vec: tuple) -> 'Point':
        dt, dp = vec
        return Point(self.tick + dt, self.key + dp, self.instrument)

    def __sub__(self, other: 'Point') -> tuple:
        if self.instrument != other.instrument:
            raise ValueError("Cannot subtract points with different instrument sets")
        return (self.tick - other.tick, self.key - other.key)

    def __repr__(self):
        return f"Point(t={self.tick}, k={self.key}, inst={self.instrument})"