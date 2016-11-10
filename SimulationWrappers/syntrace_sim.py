#!/usr/bin/python3

from simulation_wrapper import SimWrap
import subprocess
import csv

class SynTraceSim(SimWrap):
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
        self.validate_params(params)
        self.config = params

    def validate_params(self, params):
        valid_params = ["cache_size", "cpu_count"]
        if not all(k in valid_params for k in params.keys()):
            raise ValueError("Not a valid McPAT config parameter")

    def run_simulation(self, output_csv):
        pass

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        pass

def main():
    sim = SynTraceSim({"cache_size" : 2048, "cpu_count" : 8})
    sim.run()

if __name__ == "__main__":
    main()
