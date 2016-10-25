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
        self.config = params

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        filename = "stats.txt"
        self.stats = parse_stat_file(filename)

def main():
    sim = Gem5Sim({"freq" : 100})
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
