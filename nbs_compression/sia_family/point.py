from typing import Union, Tuple

Vector = Tuple[int, int]  # (dt, dp)

class Point:
    __slots__ = ('tick', 'key', 'inst_set')

    def __init__(self, tick: int, key: int, inst_set: Union[set, frozenset]):
        self.tick = tick
        self.key = key
        self.inst_set = frozenset(inst_set) if not isinstance(inst_set, frozenset) else inst_set

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return (self.tick == other.tick and
                self.key == other.key and
                self.inst_set == other.inst_set)

    def __hash__(self):
        return hash((self.tick, self.key, self.inst_set))

    def __lt__(self, other):
        if self.tick != other.tick:
            return self.tick < other.tick
        if self.key != other.key:
            return self.key < other.key
        if len(self.inst_set) != len(other.inst_set):
            return len(self.inst_set) < len(other.inst_set)
        return sorted(self.inst_set) < sorted(other.inst_set)

    def __add__(self, vec: tuple) -> 'Point':
        dt, dp = vec
        return Point(self.tick + dt, self.key + dp, self.inst_set)

    def __sub__(self, other: 'Point') -> tuple:
        if self.inst_set != other.inst_set:
            raise ValueError("Cannot subtract points with different instrument sets")
        return (self.tick - other.tick, self.key - other.key)

    def __repr__(self):
        inst_str = ','.join(str(i) for i in sorted(self.inst_set))
        return f"Point(t={self.tick}, k={self.key}, inst=[{inst_str}])"