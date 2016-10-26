#!/usr/bin/python3

from simulation_wrappers import SimWrap

import string
import re
import json

PROGRAM_LENGTH = 1000


config_defaults = { "cpu_count": 1, "cpu_frequency": 9000, "cache_size": 1024}

class MockSim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    def __init__(self, params):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """
        self.config = config_defaults
        self.set_config(params)

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
        stats = {}
        stats["Area (mm2)"] = cache_size**2
        stats["Dynamic read energy (nJ)"] = cache_size
        stats["Dynamic write energy (nJ)"] = cache_size
        stats["execution time (s)"] = ((PROGRAM_LENGTH)/(cpu_count*freq))*(1/cache_size)
        self.stats = stats

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.run_simulation()
        self.mock_stats()


def main():
    sim = MockSim({"cpu_frequency" : 1000})
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
