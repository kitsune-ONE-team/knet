#!/usr/bin/env python3
import unittest

from kitsunet.playback import PlaybackSystem
from kitsunet.snapshot import Snapshot, WorldSnapshot


class PlaybackSystemTestCase(unittest.TestCase):
    def test_update_50ms(self):
        """Update +50ms."""
        system = PlaybackSystem(20)  # tick 50ms
        system.feed_snapshot(WorldSnapshot(1))
        system.feed_snapshot(WorldSnapshot(2))
        system.update(0.050)  # +50ms
        system.update(0.050)  # +50ms
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.100)
        self.assertEqual(system.get_real_time(), 0.100)
        self.assertEqual(system.get_interpolation_factor(), 1.0)

    def test_update_120ms(self):
        """Update +120ms."""
        system = PlaybackSystem(20)  # tick 50ms
        system.feed_snapshot(WorldSnapshot(1))
        system.feed_snapshot(WorldSnapshot(2))
        system.feed_snapshot(WorldSnapshot(3))
        system.update(0.120)  # +120ms
        self.assertEqual(system.get_tick_id(), 3)
        self.assertEqual(system.get_tick_time(), 0.150)
        self.assertEqual(system.get_real_time(), 0.120)
        self.assertEqual(system.get_interpolation_factor(), 0.4)

    def test_update_49ms(self):
        """Update +49ms."""
        system = PlaybackSystem(20)  # tick 50ms
        system.feed_snapshot(WorldSnapshot(1))
        system.feed_snapshot(WorldSnapshot(2))
        system.update(0.050)  # +50ms
        system.update(0.049)  # +49ms
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.100)
        self.assertEqual(system.get_real_time(), 0.099)
        self.assertEqual(system.get_interpolation_factor(), 0.98)

    def test_feed_snapshot(self):
        """System feed snapshot."""
        system = PlaybackSystem(20)  # tick 50ms
        system.feed_snapshot(WorldSnapshot(4))
        system.feed_snapshot(WorldSnapshot(2))
        system.feed_snapshot(WorldSnapshot(10))
        system.feed_snapshot(WorldSnapshot(3))
        system.feed_snapshot(WorldSnapshot(7))
        system.feed_snapshot(WorldSnapshot(1))
        system.feed_snapshot(WorldSnapshot(6))
        system.feed_snapshot(WorldSnapshot(8))
        system.feed_snapshot(WorldSnapshot(5))
        system.feed_snapshot(WorldSnapshot(9))
        for i in range(1, 10 + 1):
            self.assertEqual(system._pull_snapshot().get_tick_id(), i)


    def test_lag(self):
        """Lag."""
        system = PlaybackSystem(20)  # tick 50ms
        system.update(0.010)  # +10ms, time stopped
        self.assertEqual(system.get_tick_time(), 0.000)
        self.assertEqual(system.get_real_time(), 0.000)
        system.feed_snapshot(WorldSnapshot(1))
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.010)
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.020)
        system.update(0.050)  # +50ms, time stopped
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.020)
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.030)
        system.feed_snapshot(WorldSnapshot(2))
        system.update(0.090)  # +90ms, time stopped, advances only +70ms
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.100)
        self.assertEqual(system.get_real_time(), 0.100)

    def test_interpolate(self):
        """Interpolate."""
        system = PlaybackSystem(20)  # tick 50ms
        system.feed_snapshot(WorldSnapshot(1, [Snapshot(entity_id=0, position=(1.0, 0, 0))]))
        system.feed_snapshot(WorldSnapshot(2, [Snapshot(entity_id=0, position=(2.0, 0, 0))]))
        system.feed_snapshot(WorldSnapshot(3, [Snapshot(entity_id=0, position=(3.0, 0, 0))]))
        system.update(0.075)  # +75ms
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.100)
        self.assertEqual(system.get_real_time(), 0.075)
        self.assertEqual(system.get_interpolation_factor(), 0.5)
        self.assertEqual(
            system.get_interpolated_snapshot().get_snapshot(0).get_position(),
            (1.5, 0, 0))
        system.update(0.015)  # +15ms
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.100)
        self.assertEqual(system.get_real_time(), 0.090)
        self.assertEqual(system.get_interpolation_factor(), 0.8)
        self.assertEqual(
            system.get_interpolated_snapshot().get_snapshot(0).get_position(),
            (1.8, 0, 0))
        system.update(0.035)  # +35ms
        self.assertEqual(system.get_tick_id(), 3)
        self.assertEqual(system.get_tick_time(), 0.150)
        self.assertEqual(system.get_real_time(), 0.125)
        self.assertEqual(system.get_interpolation_factor(), 0.5)
        self.assertEqual(
            system.get_interpolated_snapshot().get_snapshot(0).get_position(),
            (2.5, 0, 0))

    def test_overflow(self):
        """Overflow."""
        system = PlaybackSystem(20)  # tick 50ms
        system.feed_snapshot(WorldSnapshot(1))
        system.feed_snapshot(WorldSnapshot(2))
        system.feed_snapshot(WorldSnapshot(3))
        system.feed_snapshot(WorldSnapshot(4))
        self.assertEqual(system.get_snapshot_queue_size(), 4)
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_snapshot_queue_size(), 1)
        system.update(0.020)  # +20ms
        self.assertEqual(system.get_snapshot_queue_size(), 1)
        system.update(0.040)  # +40ms
        self.assertEqual(system.get_snapshot_queue_size(), 0)


if __name__ == '__main__':
    unittest.main()
