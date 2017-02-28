#!/usr/bin/python3

from simulation_wrapper import SimWrap

import string
import re
import json

PROGRAM_LENGTH = 1000


config_defaults = { "cpu_count": 1, "cpu_frequency": 9000, "cache_size": 1024}

def default_config_to_stats(cpu_count, freq, cache_size):
    stats = {}
    stats["Area (mm2)"] = cache_size**2
    stats["Dynamic read energy (nJ)"] = cache_size
    stats["Dynamic write energy (nJ)"] = cache_size
    stats["execution time (s)"] = ((PROGRAM_LENGTH)/(cpu_count*freq))*(1/cache_size)

    return stats

class MockSim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    # TODO: rename params
    def __init__(self, params, config_to_stats = default_config_to_stats):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """
        self.config = config_defaults
        self.set_config(params)
        self.config_to_stats = config_to_stats

    def set_config(self, params):
        """
        Updates the system configuration with the passed parameters
        """
        self.validate_params(params)
        for k in params.keys():
            self.config[k] = params[k]

    def validate_params(self, params):
        valid_params = [ "cpu_count", "cpu_frequency", "cache_size"]
        if not all(k in valid_params for k in params.keys()):
            raise ValueError("Not a valid mock_sim config parameter")

    def run_simulation(self):
        pass

    def mock_stats(self):
        cpu_count = self.config["cpu_count"]
        freq = self.config["cpu_frequency"]
        cache_size = self.config["cache_size"]
        self.stats = self.config_to_stats(cpu_count, freq, cache_size)

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.run_simulation()
        self.mock_stats()


def many_peaks(cpu_count, freq, cache_size):
    """
    Creates an interesting topology by zeroing execution time
    as specific cpu_count values
    """
    stats = {}
    stats["Area (mm2)"] = cache_size**2
    stats["Dynamic read energy (nJ)"] = cache_size
    stats["Dynamic write energy (nJ)"] = cache_size
    stats["execution time (s)"] = ((PROGRAM_LENGTH)/(cpu_count*freq))*(1/cache_size)
    if cpu_count in [1, 5, 7]:
        stats["execution time (s)"] = 0

    return stats

class ManyPeaksMockSim(MockSim):
    """
    Creates a MockSim that is designed to have search parties find different
    peaks. The many_peaks functon mocks stats are minimal at [1, 5, 7] cpu
    cores.
    """

    def __init__(self, params):
        super().__init__(params, many_peaks)


def main():
    sim = MockSim({"cpu_frequency" : 1000})
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
