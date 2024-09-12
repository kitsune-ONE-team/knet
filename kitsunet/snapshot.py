from typing import Self

from .math import add3, div3, lerp3
from .event import Event


class Snapshot:
    """
    Game entity state.
    """
    _entity_id: int
    _position: tuple[float]

    def __init__(self, entity_id: int = 0, position: tuple[float] | None = None):
        self._entity_id = entity_id
        self._position = position or (0.0, 0.0, 0.0)

    def __str__(self) -> str:
        return f'Snapshot #{self.get_entity_id()} {self.get_position()}'

    def get_entity_id(self) -> int:
        return self._entity_id

    def get_position(self) -> tuple[float]:
        return self._position

    def interpolate(self, snapshot: Self, factor: float) -> Self:
        """
        Get iterpolated snapshot between current one and another one.

        :param snapshot: snapshot to interpolate into
        :type snapshot: :class:`kitsunet.snapshot.Snapshot`

        :param factor: interpolation factor
        :type factor: float

        :returns: interpolated snapshot
        :rtype: :class:`kitsunet.snapshot.Snapshot`
        """
        return self.__class__(
            entity_id=self.get_entity_id(),
            position=lerp3(self.get_position(), snapshot.get_position(), factor)
        )

    def extrapolate(self, event: Event, dt: float) -> Self:
        """
        Get iterpolated snapshot between current one and another one.

        :param snapshot: snapshot to interpolate into
        :type snapshot: :class:`kitsunet.snapshot.Snapshot`

        :param factor: interpolation factor
        :type factor: float

        :returns: interpolated snapshot
        :rtype: :class:`kitsunet.snapshot.Snapshot`
        """
        new_position: tuple[float] = self.get_position()
        if dt != 0:
            new_position: tuple[float] = add3(new_position, div3(event.get_velocity(), (dt, dt, dt)))

        return self.__class__(
            entity_id=self.get_entity_id(),
            position=new_position,
        )


class WorldSnapshot:
    """
    Game world state.
    """
    _tick_id: int
    _snapshots: dict

    def __init__(self, tick_id: int, snapshots: tuple[Snapshot] | list[Snapshot] | None = None):
        self._tick_id = tick_id
        self._snapshots = {}
        for snapshot in (snapshots or []):
            self._snapshots[snapshot.get_entity_id()] = snapshot

    def __str__(self) -> str:
        return f'WorldSnapshot #{self.get_tick_id()} ({len(self.get_entity_ids())})'

    def get_tick_id(self) -> int:
        return self._tick_id

    def get_entity_ids(self) -> frozenset[int]:
        return frozenset(self._snapshots.keys())

    def add_snapshot(self, entity_id: int, snapshot: Snapshot):
        self._snapshots[entity_id] = snapshot

    def get_snapshot(self, entity_id: int) -> Snapshot | None:
        return self._snapshots.get(entity_id)

    def interpolate(self, wsnapshot: Self, factor: float) -> Self:
        snapshots: list[Snapshot] = []

        for entity_id in self.get_entity_ids():
            snapshot_a: Snapshot = self.get_snapshot(entity_id)
            snapshot_b: Snapshot = wsnapshot.get_snapshot(entity_id)
            if snapshot_a and snapshot_b:
                snapshots.append(snapshot_a.interpolate(snapshot_b, factor))

        return self.__class__(
            tick_id=self.get_tick_id(),
            snapshots=snapshots,
        )

    def extrapolate(self, events: list[Event], dt: float, tick_id: int | None) -> Self:
        snapshots: list[Snapshot] = []

        for event in events:
            snapshot: Snapshot = self.get_snapshot(event.get_entity_id())
            if snapshot:
                snapshots.append(snapshot.extrapolate(event, dt))

        return self.__class__(
            # tick_id=self.get_tick_id() + 1,
            tick_id=self.get_tick_id() if tick_id is None else tick_id,
            snapshots=snapshots,
        )
