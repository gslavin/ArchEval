#!/usr/bin/python3

from simulation_wrappers import SimWrap

import string
import re
import json

def parse_stat_file(filename):
    """
    Parses the gem5 stat.txt file and returns the
    indicated fields.  Currently only works for
    op classes
    """
    with open(filename, 'r') as f:
        stats = {'op_class':{}}
        params = ['op_class']
        for line in f:
            # strip out comment
            line = line.split("#")[0].strip()
            #Split into fields
            fields = re.split(' +', line)
            name = fields[0]

            # Get class, field names, and field values
            if any(x in name for x in params):
                key = re.split('[.:]+', name)[2]
                var = re.split('[.:]+', name)[3]
                val = fields[1]
                stats[key][var] = val
    return stats

class Gem5Sim(SimWrap):
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
        valid_params = [ "cpu_count", "cpu_frequency", "cache_size"]
        if not all(k in valid_params for k in params.keys()):
            raise ValueError("Not a valid gem5 config parameter")

    def run_simulation(self):
        pass

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.run_simulation()

        # Collect the statistics
        filename = "stats.txt"
        self.stats = parse_stat_file(filename)

def main():
    sim = Gem5Sim({"cpu_frequency" : 100})
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
