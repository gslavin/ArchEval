#!/usr/bin/env python3

import unittest
import defs

from mock_sim import MockSim
from mcpat_sim import McPatSim
from gem5_sim import Gem5Sim
from syntrace_sim import SynchroTraceSim


default_benchmark = defs.ROOT_DIR + "/Tests/test-progs/random_access/random_access"
default_options = "10000"

class TestMockSim(unittest.TestCase):
    def test_valid_args(self):
        """
        Valid arguments should not raise an exception
        """
        MockSim({"cpu_frequency" : 1000})

    def test_invalid_args(self):
        """
        Invalid arguments should raise an exception
        """
        with self.assertRaises(ValueError):
            MockSim({"fake_arg": 100})

    def test_different_args_different_results(self):
        """
        Different cache sizes should give different results
        """
        sim_small = MockSim({"cache_size" : 2048})
        sim_large = MockSim({"cache_size" : 4096})

        sim_small.run()
        sim_large.run()
        self.assertNotEqual(sim_small.stats, sim_large.stats)

class TestMcPatSim(unittest.TestCase):
    def test_valid_args(self):
        """
        Valid arguments should not raise an exception
        """
        McPatSim({"cache_size" : 2048})

    def test_one_invalid_arg(self):
        """
        Invalid arguments should raise an exception
        """
        McPatSim({"fake_arg": 56, "cache_size" : 2048})

    def test_all_invalid_args(self):
        """
        Invalid arguments should raise an exception
        """
        with self.assertRaises(ValueError):
            McPatSim({"fake_arg": 56, "other_fake_arg" : 2048})

    def test_sim_run(self):
        """
        Sim object should be run without raising an exception
        """
        sim = McPatSim({"cache_size" : 2048})
        sim.run()

    def test_sim_stats(self):
        """
        The output statistics should have all the expected fields
        """
        sim = McPatSim({"cache_size" : 2048})
        sim.run()
        self.assertNotEqual(sim.stats, None)

        fields = ["Area (mm2)", "Dynamic read energy (nJ)", "Dynamic write energy (nJ)"]
        self.assertTrue(all(k in fields for k in sim.stats))

    def test_cache_size_variation(self):
        """
        Different cache sizes should give different results
        """
        sim_small = McPatSim({"cache_size" : 2048})
        sim_large = McPatSim({"cache_size" : 4096})

        sim_small.run()
        sim_large.run()
        self.assertNotEqual(sim_small.stats, sim_large.stats)

class TestGem5Sim(unittest.TestCase):
    def test_sim_stats(self):
        sim = Gem5Sim(default_benchmark, default_options)
        sim.run()
        self.assertNotEqual(sim.stats, None)

class TestSynchrotraceSim(unittest.TestCase):
    def test_sim_stats(self):
        sim = SynchroTraceSim()
        sim.run()
        self.assertNotEqual(sim.stats, None)



if __name__ == '__main__':
    unittest.main()
