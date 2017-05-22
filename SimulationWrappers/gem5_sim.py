#!/usr/bin/env python3

from simulation_wrapper import SimWrap

import string
import re
import json
import subprocess
import defs
import os
import time

config_defaults = { "cpu_count": 1, "cpu_frequency": 9000000, "cache_size": 1024}
valid_sys_config_params = [ "cpu_count", "cpu_frequency", "cache_size" ]

def nested_stats_insert(stats, fields):
    # Expecting lines with at least 2 fields separated by whitespace
    if len(fields) < 2:
        return

    #
    # First field is the key, which may have nested attributes
    # Nested attributes are indicated by the fully qualified name separated by '.'
    # i.e. 'system.voltage_domain.voltage'
    #
    if ("." in fields[0]):
        # Split out the fully qualified name of the attribute
        nested_keys = fields[0].split(".")
        # Retrieve the outermost domain name
        domain = nested_keys[0]

        #
        # If this domain has been encoutered before, grab the existing dict
        # Otherwise, create a new one
        #
        if (domain in stats.keys()):
            nest = stats[domain]
        else:
            nest = {}

        # Strip the outermost domain from the fully qualified name
        nested_keys.pop(0)

        # Insert this value into the nest using the remaining domains
        nested_stats_insert(nest, [".".join(nested_keys), fields[1]])

        # Update the main dictionary with this updated nested dictionary
        stats[domain] = nest

    else:
        stats[fields[0]] = gem5_parse_value(fields[1])

def gem5_parse_value(string):
    if ("." in string or "nan" in string):
        return float(string)
    return int(string)

def gem5_parse_freq(freq):
    prefix = ""

    if (freq >= 1000):
        freq = int(freq / 1000)
        prefix = "K"


    if (freq >= 1000):
        freq = int(freq / 1000)
        prefix = "M"


    if (freq >= 1000):
        freq = int(freq / 1000)
        prefix = "G"

    return str(freq) + prefix + "Hz"

def gem5_parse_cache(freq):
    prefix = ""

    if (freq >= 1024):
        freq = int(freq / 1024)
        prefix = "k"


    if (freq >= 1024):
        freq = int(freq / 1024)
        prefix = "m"


    if (freq >= 1024):
        freq = int(freq / 1024)
        prefix = "g"

    return str(freq) + prefix + "B"


class Gem5Sim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats ## dict of information
        simulation results
    """

    def __init__(self, benchmark, options, sys_config = config_defaults):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """

        if (len(defs.GEM5_DIR) == 0):
            raise ValueError("Please update Gem5 directory in defs.py.")

        self.config = {}
        self.set_config(sys_config)
        self.benchmark = benchmark
        self.options = options

    def set_config(self, sys_config):
        """
        Updates the system configuration with the passed parameters
        """
        self.validate_sys_config(sys_config)
        for k in sys_config.keys():
            self.config[k] = sys_config[k]

    def validate_sys_config(self, sys_config):
        if not all(k in valid_sys_config_params for k in sys_config.keys()):
            raise ValueError("Not a valid gem5 config parameter")

        pass

    def run_simulation(self):
        #CPU_TYPE = """ --cpu-type="DerivO3CPU" """
        #RUBY = " --ruby"
        #NUM_CPUS = " -n " + str(self.config["cpu_count"])
        #FREQ = " --cpu-clock=" + gem5_parse_freq(self.config["cpu_frequency"])
        #L1_CACHE = " --l1d_size=" + gem5_parse_cache(self.config["cache_size"])
        #OUTPUT = " -d " + defs.ROOT_DIR
        #OUTPUT = " --stats-file=" + defs.ROOT_DIR + "/stats.txt"
        #COMMAND = " -c " + defs.BENCHMARK_PATH

        subprocess.run("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} >> {10}".format(\
                                defs.GEM5_DIR + "/build/X86/gem5.opt", \
                                "--stats-file=" + defs.ROOT_DIR + "/stats.txt", \
                                "-r", \
                                defs.GEM5_DIR + "/configs/example/se.py", \
                                """--cpu-type="DerivO3CPU" """, \
                                "--ruby", \
                                " -n " + str(self.config["cpu_count"]), \
                                "--cpu-clock=" + gem5_parse_freq(self.config["cpu_frequency"]), \
                                "--l1d_size=" + gem5_parse_cache(self.config["cache_size"]), \
                                "-c " + self.benchmark + " --options=" + self.options, \
                                defs.LOG_DIR + "/gem5.log"), shell=True)
        subprocess.check_call("/bin/cat " + defs.ROOT_DIR + "/m5out/simout >> " + defs.LOG_DIR + "/gem5.log", shell=True)
        #pass
        with open(defs.LOG_DIR + '/gem5.log', 'r') as f:
            for line in f:
                pass
            ret_code = line.strip()
            if ret_code != "0":
                raise ValueError("Bad gem5 return code: {}".format(ret_code))

    def parse_stats(self, filename):
        stats = {}

        f = open(filename, 'r')

        try:
            # First two lines of stat file are not data, but let's be smart
            # about it and instead search for the start of data indicator
            while ("Begin Simulation Statistics" not in f.readline()):
                continue

            s = f.readline()
            while (s != "" and "End Simulation Statistics" not in s):
                # TODO FIXME incorporate new line formats into parser
                if ("::" in s or "|" in s):
                    s = f.readline()
                    continue

                nested_stats_insert(stats, s.split())

                s = f.readline()

        finally:
            f.close()

        return stats

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.run_simulation()

        # Collect the statistics
        filename = defs.ROOT_DIR + "/stats.txt"
        self.stats = self.parse_stats(filename)
        os.remove(filename)

def main():
    sim = Gem5Sim()
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
