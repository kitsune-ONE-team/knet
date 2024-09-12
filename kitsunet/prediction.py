from .event import Event
from .playback import PlaybackSystem
from .snapshot import Snapshot, WorldSnapshot


class PredictionSystem(PlaybackSystem):
    """
    Interactive playback system which can playback snapshots,
    generate input events and predict future state.
    """
    _initial_snapshot: WorldSnapshot
    _local_entity_id: int
    _local_event_queue: list[Event]
    _local_event_history: list[tuple[Event, WorldSnapshot]]
    _event_class: type
    _event_kwargs: dict

    def __init__(
            self, tick_rate: int, initial_snapshot: WorldSnapshot = None,
            local_entity_id: int = 0, event_class: type = None,
            event_kwargs: dict = None):
        """
        Create a new prediction system.

        :param tick_rate: tick rate in Hz, ex.: 20Hz
        :type tick_rate: int
        """
        super().__init__(tick_rate)
        self._local_entity_id = local_entity_id
        self._local_event_queue = []
        self._local_event_history = []
        self._initial_snapshot = initial_snapshot or WorldSnapshot(tick_id=0)
        self._event_class = event_class or Event
        self._event_kwargs = event_kwargs or {}

    def feed_event(self, event: Event):
        """
        Feed event into queue.

        :param event: event
        :type event: :class:`kitsunet.event.Event`
        """
        self._local_event_queue.append(event)

    def get_event_queue_size(self) -> int:
        """
        Get event queue size.

        :returns: number of events in queue
        :rtype: int
        """
        return len(self._local_event_queue)

    def _pull_event(self, pop: bool = False) -> Event | None:
        """
        Pull event from the queue.

        :param pop: delete event from queue?
        :type pop: bool

        :returns: event
        :rtype: :class:`kitsunet.event.Event`
        """
        if self._local_event_queue:
            if pop:
                return self._local_event_queue.pop(-1)
            else:
                return self._local_event_queue[-1]

    def _remote_entity_extrapolate(self) -> WorldSnapshot:
        """
        Remote entity extrapolation.
        Extrapolates remote entity state in case of missing snapshot.
        """
        events: list[Event] = []
        for entity_id in self._next_snapshot.get_entity_ids():
            if entity_id == self._local_entity_id:
                continue

            events.append(self._event_class(
                tick_id=self.get_tick_id(),
                entity_id=entity_id,
                **self._event_kwargs,
            ))

        return self._next_snapshot.extrapolate(events, self._tick_duration / 1000)

    def _client_side_predict(self) -> tuple[Event, Snapshot]:
        """
        Client side prediction (CSP).
        Extrapolates remote entity state using input events.
        """
        event: Event = self._pull_event()
        if not event:
            event = self._event_class(
                tick_id=self.get_tick_id(),
                entity_id=self._local_entity_id,
                **self._event_kwargs,
            ))

        if self._local_event_history:
            _, local_wsnapshot: WorldSnapshot = self._local_event_history[-1]
        else:
            local_wsnapshot: WorldSnapshot = self._next_snapshot

        snapshot: Snapshot = local_wsnapshot.get_snapshot(self._local_entity_id)
        return snapshot.extrapolate([event], self._tick_duration / 1000)

    def _pull_snapshot(self) -> WorldSnapshot:
        wsnapshot: WorldSnapshot = super()._pull_snapshot()

        if not self._next_snapshot:
            self._next_snapshot = self._initial_snapshot

        if not wsnapshot:
            wsnapshot = self._remote_entity_extrapolate()

        event, snapshot: tuple[Event, Snapshot] = self._client_side_predict()
        wsnapshot.add_snapshot(self._local_entity_id, snapshot)
        self._local_event_history.append((event, wsnapshot))

        return wsnapshot

    def _drop_events(self):
        """Clears events queue."""
        while self.get_event_queue_size() > 1:
            self._pull_event(pop=True)

    def update(self, dt: float):
        super().update(dt)

        # clear events queue
        self._drop_events()
