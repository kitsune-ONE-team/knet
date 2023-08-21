def lerp(a: float, b: float, factor: float) -> float:
    return a * (1 - factor) + b * factor


def lerp3(a: list[float], b: list[float], factor: float) -> list[float]:
    return [
        lerp(a[0], b[0], factor),
        lerp(a[1], b[1], factor),
        lerp(a[2], b[2], factor),
    ]


class Snapshot:
    """
    Game world state.
    """
    _tick_id: int
    _position: list[float]

    def __init__(self, tick_id: int, position: list[float] | None = None):
        self._tick_id = tick_id
        self._position = position or [0.0, 0.0, 0.0]

    def __str__(self) -> str:
        return f'Snapshot #{self.get_tick_id()} {self.get_position()}'

    def get_tick_id(self) -> int:
        return self._tick_id

    def get_position(self) -> list[float]:
        return self._position

    def lerp(self, snapshot, factor: float):
        return self.__class__(
            tick_id=self._tick_id,
            position=lerp3(self.get_position(), snapshot.get_position(), factor),
        )
