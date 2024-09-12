class Event:
    """
    Input/command event.
    """
    _tick_id: int
    _entity_id: int
    _velocity: tuple[float]

    def __init__(self, tick_id: int, entity_id: int, velocity: tuple[float] | None = None):
        self._tick_id = tick_id
        self._entity_id = entity_id
        self._velocity = velocity or (0.0, 0.0, 0.0)

    def __str__(self) -> str:
        return f'Event #{self.get_tick_id()} {self.get_velocity()}'

    def get_tick_id(self) -> int:
        return self._tick_id

    def get_entity_id(self) -> int:
        return self._entity_id

    def get_velocity(self) -> tuple[float]:
        return self._velocity
