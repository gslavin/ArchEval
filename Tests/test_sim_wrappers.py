#!/usr/bin/python3

import unittest

from mock_sim import MockSim
from mcpat_sim import McPatSim

class TestMockSim(unittest.TestCase):
    def test_valid_args(self):
    	MockSim({"cpu_frequency" : 1000})

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            MockSim({"fake_arg": 100})

class TestMcPatSim(unittest.TestCase):
    def test_valid_args(self):
        McPatSim({"cache_size" : 2048})

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            McPatSim({"fake_arg": 56, "cache_size" : 2048})

    def test_sim_run(self):
        sim = McPatSim({"cache_size" : 2048})
        sim.run()

if __name__ == '__main__':
    unittest.main()
