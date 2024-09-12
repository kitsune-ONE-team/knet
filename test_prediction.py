#!/usr/bin/env python3
import unittest

from kitsunet.event import Event
from kitsunet.prediction import PredictionSystem
from kitsunet.snapshot import Snapshot, WorldSnapshot


class PredictionSystemTestCase(unittest.TestCase):
    def test_extrapolate(self):
        """Extrapolate."""
        system = PredictionSystem(20)  # tick 50ms
        system.update(0.018)  # +18ms, extrapolated
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.018)
        self.assertEqual(system.get_interpolation_factor(), 0.36)
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.028)
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_tick_id(), 1)
        self.assertEqual(system.get_tick_time(), 0.050)
        self.assertEqual(system.get_real_time(), 0.038)
        system.update(0.050)  # +50ms, extrapolated
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.100)
        self.assertEqual(system.get_real_time(), 0.088)
        system.update(0.010)  # +10ms
        self.assertEqual(system.get_tick_id(), 2)
        self.assertEqual(system.get_tick_time(), 0.1)
        self.assertEqual(system.get_real_time(), 0.098)
        system.update(0.090)  # +90ms, extrapolated
        self.assertEqual(system.get_tick_id(), 4)
        self.assertEqual(system.get_tick_time(), 0.200)
        self.assertEqual(system.get_real_time(), 0.188)


if __name__ == '__main__':
    unittest.main()
