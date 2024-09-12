from .event import Event
from .playback import PlaybackSystem
from .snapshot import Snapshot, WorldSnapshot


class ExtrapolationSystem(PlaybackSystem):
    """
    Interactive playback system which can playback snapshots,
    generate input events and predict future state.
    """
    _initial_snapshot: WorldSnapshot

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

    def _pull_snapshot(self) -> WorldSnapshot:
        wsnapshot: WorldSnapshot = super()._pull_snapshot()

        if not self._next_snapshot:
            return False
            # self._next_snapshot = self._initial_snapshot

        if not wsnapshot:
            wsnapshot = self._remote_entity_extrapolate()

        event, snapshot: tuple[Event, Snapshot] = self._client_side_predict()
        wsnapshot.add_snapshot(self._local_entity_id, snapshot)
        self._local_event_history.append((event, wsnapshot))

        return wsnapshot
