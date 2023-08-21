#!/usr/bin/env python3
import unittest

from knet.player import Player
from knet.snapshot import Snapshot


class PlayerTestCase(unittest.TestCase):
    def test_player_50ms(self):
        """player +50ms"""
        player = Player(20)  # tick 50ms
        player.feed_snapshot(Snapshot(1))
        player.feed_snapshot(Snapshot(2))
        player.update(0.050)  # +50ms
        player.update(0.050)  # +50ms
        self.assertEqual(player.get_tick_id(), 2)
        self.assertEqual(player.get_tick_time(), 0.100)
        self.assertEqual(player.get_real_time(), 0.100)
        self.assertEqual(player.get_interpolation_factor(), 1.0)

    def test_player_120ms(self):
        """player +120ms"""
        player = Player(20)  # tick 50ms
        player.feed_snapshot(Snapshot(1))
        player.feed_snapshot(Snapshot(2))
        player.feed_snapshot(Snapshot(3))
        player.update(0.120)  # +120ms
        self.assertEqual(player.get_tick_id(), 3)
        self.assertEqual(player.get_tick_time(), 0.150)
        self.assertEqual(player.get_real_time(), 0.120)
        self.assertEqual(player.get_interpolation_factor(), 0.4)

    def test_player_49ms(self):
        """player +49ms"""
        player = Player(20)  # tick 50ms
        player.feed_snapshot(Snapshot(1))
        player.feed_snapshot(Snapshot(2))
        player.update(0.050)  # +50ms
        player.update(0.049)  # +49ms
        self.assertEqual(player.get_tick_id(), 2)
        self.assertEqual(player.get_tick_time(), 0.100)
        self.assertEqual(player.get_real_time(), 0.099)
        self.assertEqual(player.get_interpolation_factor(), 0.98)

    def test_player_feed(self):
        """player feed"""
        player = Player(20)  # tick 50ms
        player.feed_snapshot(Snapshot(4))
        player.feed_snapshot(Snapshot(2))
        player.feed_snapshot(Snapshot(10))
        player.feed_snapshot(Snapshot(3))
        player.feed_snapshot(Snapshot(7))
        player.feed_snapshot(Snapshot(1))
        player.feed_snapshot(Snapshot(6))
        player.feed_snapshot(Snapshot(8))
        player.feed_snapshot(Snapshot(5))
        player.feed_snapshot(Snapshot(9))
        for i in range(1, 10 + 1):
            self.assertEqual(player._pull_snapshot().get_tick_id(), i)

    def test_player_lag(self):
        """player lag"""
        player = Player(20)  # tick 50ms
        player.update(0.010)  # +10ms, time stopped
        self.assertEqual(player.get_tick_time(), 0.000)
        self.assertEqual(player.get_real_time(), 0.000)
        player.feed_snapshot(Snapshot(1))
        player.update(0.010)  # +10ms
        self.assertEqual(player.get_tick_id(), 1)
        self.assertEqual(player.get_tick_time(), 0.050)
        self.assertEqual(player.get_real_time(), 0.010)
        player.update(0.010)  # +10ms
        self.assertEqual(player.get_tick_id(), 1)
        self.assertEqual(player.get_tick_time(), 0.050)
        self.assertEqual(player.get_real_time(), 0.020)
        player.update(0.050)  # +50ms, time stopped
        self.assertEqual(player.get_tick_id(), 1)
        self.assertEqual(player.get_tick_time(), 0.050)
        self.assertEqual(player.get_real_time(), 0.020)
        player.update(0.010)  # +10ms
        self.assertEqual(player.get_tick_id(), 1)
        self.assertEqual(player.get_tick_time(), 0.050)
        self.assertEqual(player.get_real_time(), 0.030)
        player.feed_snapshot(Snapshot(2))
        player.update(0.090)  # +90ms, advances only +70ms
        self.assertEqual(player.get_tick_id(), 2)
        self.assertEqual(player.get_tick_time(), 0.100)
        self.assertEqual(player.get_real_time(), 0.100)

    def test_player_lerp(self):
        """player feed"""
        player = Player(20)  # tick 50ms
        player.feed_snapshot(Snapshot(1, [1.0, 0, 0]))
        player.feed_snapshot(Snapshot(2, [2.0, 0, 0]))
        player.feed_snapshot(Snapshot(3, [3.0, 0, 0]))
        player.update(0.075)  # +75ms
        self.assertEqual(player.get_tick_id(), 2)
        self.assertEqual(player.get_tick_time(), 0.100)
        self.assertEqual(player.get_real_time(), 0.075)
        self.assertEqual(player.get_interpolation_factor(), 0.5)
        self.assertEqual(player.get_interpolated_snapshot().get_position(), [1.5, 0, 0])
        player.update(0.015)  # +15ms
        self.assertEqual(player.get_tick_id(), 2)
        self.assertEqual(player.get_tick_time(), 0.100)
        self.assertEqual(player.get_real_time(), 0.090)
        self.assertEqual(player.get_interpolation_factor(), 0.8)
        self.assertEqual(player.get_interpolated_snapshot().get_position(), [1.8, 0, 0])
        player.update(0.035)  # +35ms
        self.assertEqual(player.get_tick_id(), 3)
        self.assertEqual(player.get_tick_time(), 0.150)
        self.assertEqual(player.get_real_time(), 0.125)
        self.assertEqual(player.get_interpolation_factor(), 0.5)
        self.assertEqual(player.get_interpolated_snapshot().get_position(), [2.5, 0, 0])

    def test_player_overflow(self):
        """player overflow"""
        player = Player(20)  # tick 50ms
        player.feed_snapshot(Snapshot(1))
        player.feed_snapshot(Snapshot(2))
        player.feed_snapshot(Snapshot(3))
        player.feed_snapshot(Snapshot(4))
        self.assertEqual(player.get_snapshot_queue_size(), 4)
        player.update(0.010)  # +10ms
        self.assertEqual(player.get_snapshot_queue_size(), 1)
        player.update(0.020)  # +20ms
        self.assertEqual(player.get_snapshot_queue_size(), 1)
        player.update(0.040)  # +40ms
        self.assertEqual(player.get_snapshot_queue_size(), 0)


if __name__ == '__main__':
    unittest.main()
