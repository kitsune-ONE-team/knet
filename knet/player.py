from .snapshot import Snapshot


class Player:
    """
    Playback system which plays the queued snapshots.
    """
    _snapshot_queue: list[Snapshot]
    _tick_rate: int  # in Hz
    _tick_duration: float  # in ms

    _next_snapshot: Snapshot | None
    _prev_snapshot: Snapshot | None
    _intr_snapshot: Snapshot | None

    _tick_time: float  # in ms
    _real_time: float  # in ms

    def __init__(self, tick_rate: int):
        """
        Create a new playback system.

        :param tick_rate: tick rate in Hz, ex.: 20Hz
        :type tick_rate: int
        """
        self._snapshot_queue = []
        self._tick_rate = tick_rate  # ex.: 20Hz
        self._tick_duration = 1 / tick_rate * 1000  # ex.: 1 / 20 * 1000 = 50ms

        self._next_snapshot = None
        self._prev_snapshot = None
        self._intr_snapshot = None

        self._tick_time = 0
        self._real_time = 0

    def __str__(self) -> str:
        return f'Player {self._tick_rate}Hz'

    def feed_snapshot(self, snapshot: Snapshot):
        """
        Feed snapshot into queue.

        :param snapshot: snapshot
        :type snapshot: :class:`knet.snapshot.Snapshot`
        """
        if snapshot.get_tick_id() <= self.get_tick_id():  # outdated
            return

        for i in range(len(self._snapshot_queue)):
            if snapshot.get_tick_id() == self._snapshot_queue[i].get_tick_id():  # same
                break

            if snapshot.get_tick_id() > self._snapshot_queue[i].get_tick_id():  # newer
                self._snapshot_queue.insert(i, snapshot)
                break

        else:  # did not matched, add anyway
            self._snapshot_queue.append(snapshot)

    def get_tick_id(self) -> int:
        """
        Get tick ID of the next snapshot.

        :returns: tick ID
        :rtype: int
        """
        if self._next_snapshot:
            return self._next_snapshot.get_tick_id()
        return 0

    def get_tick_time(self) -> float:
        """
        Get time of the next tick in seconds.

        :returns: time in seconds
        :rtype: float
        """
        return self._tick_time / 1000

    def get_real_time(self) -> float:
        """
        Get real time in seconds.

        :returns: time in seconds
        :rtype: float
        """
        return self._real_time / 1000

    def get_interpolation_factor(self) -> float:
        """
        Get interpolation factor between previos and next snapshot.

        :returns: interpolcation factor from 0.0 to 1.0
        :rtype: float
        """
        if not self._prev_snapshot:
            return 1.0

        # tick_delta: int = (
        #     self._next_snapshot.get_tick_id() -
        #     self._prev_snapshot.get_tick_id())
        time_remaining: float = self._tick_time - self._real_time
        last_factor: float = 1 - time_remaining / self._tick_duration
        # if tick_delta <= 1:
        if True:
            return last_factor
        else:
            return (last_factor + tick_delta - 1) / tick_delta

    def get_snapshot_queue_size(self) -> int:
        """
        Get snapshot queue size.

        :returns: number of snapshots in queue
        :rtype: int
        """
        return len(self._snapshot_queue)

    def get_interpolated_snapshot(self) -> Snapshot | None:
        """
        Get a snapshot which is a result of interpolation.

        :returns: snapshot
        :rtype: :class:`knet.snapshot.Snapshot`
        """
        return self._intr_snapshot

    def _pull_snapshot(self) -> Snapshot | None:
        """
        Pull snapshot with lowest tick ID.

        :returns: snapshot
        :rtype: :class:`knet.snapshot.Snapshot`
        """
        if self._snapshot_queue:
            return self._snapshot_queue.pop(-1)

    def _do_step(self):
        snapshot: Snapshot = self._pull_snapshot()
        if not snapshot:
            return False

        self._prev_snapshot = self._next_snapshot
        self._next_snapshot = snapshot
        return True

    def update(self, dt: float):
        """
        Advances time.

        :param dt: delta time in seconds
        :type dt: float
        """
        real_time_new: float = self._real_time + (dt * 1000)
        while self._tick_time < real_time_new:
            if self._do_step():
                self._tick_time += self._tick_duration
                self._real_time = max(self._real_time, self._tick_time)
            else:
                break
        else:
            self._real_time = real_time_new

        factor: float = self.get_interpolation_factor()
        if factor == 1.0:
            self._intr_snapshot = self._next_snapshot
        else:
            self._intr_snapshot = self._prev_snapshot.lerp(self._next_snapshot, factor)

        while self.get_snapshot_queue_size() > 1:
            self._pull_snapshot()
