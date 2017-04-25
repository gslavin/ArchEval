#!/usr/bin/python3

from simulation_wrapper import SimWrap
import subprocess
import csv
import defs
import os


config_defaults = { "cpu_count": 1, "cpu_frequency": 9000000,  \
    "cache_size": 1024}
valid_sys_config_params = \
    [ "cpu_count", "cpu_frequency", "cache_size" ]

# TODO: combine common gem5/Synchrotrace functions into a parent class

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



class SynchroTraceSim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats
        simulation results
    """

    def __init__(self, event_dir = defs.EVENT_DIR,
            sys_config = config_defaults):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """

        if (len(defs.SYNCHROTRACE_DIR) == 0):
            raise ValueError("Please update Synchrotrace directory in defs.py.")

        self.config = {}
        self.set_config(sys_config)
        self.event_dir = event_dir

    # TODO: move this function into the SimWrap class
    def set_config(self, sys_config):
        """
        Updates the system configuration with the passed parameters
        """
        self.validate_sys_config(sys_config)
        for k in sys_config.keys():
            self.config[k] = sys_config[k]

    def validate_sys_config(self, sys_config):
        if not all(k in valid_sys_config_params
                for k in sys_config.keys()):
            raise ValueError("Not a valid gem5 config parameter")

        pass

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

    def run_simulation(self):

        subprocess.check_call("{0} {1} {2} {3} {4} {5} {6} {7} {8} "
            "{9} {10} {11} {12} {13} >> {14}".format( \
            defs.SYNCHROTRACE_DIR + "/build/X86_MESI_Two_Level/gem5.opt", \
            "-r", \
            defs.SYNCHROTRACE_DIR + "/configs/example/synchrotrace_ruby.py", \
            "--ruby", \
            "--network=garnet2.0", \
            # TODO: Modify the topology
            "--topology=Mesh_XY", \
            # TODO: Modify the mesh rows
            "--mesh-rows=1", \
            "--event-dir=" + self.event_dir, \
            "--output-dir=" + defs.ROOT_DIR + "/_OutSynchrotrace", \
            "--num-cpus=1", \
            "--num-threads=1", \
            "--num-dirs=8", \
            "--num-l2caches=8", \
            "--l1d_size=64kB --l1d_assoc=2 --l1i_size=64kB --l1i_assoc=2 --l2_size=4096kB --l2_assoc=8", \
            "--cpi-iops=1 --cpi-flops=1", \
            "--bandwidth-factor=4 --master-freq=1 --cacheline_size=64", \
            defs.LOG_DIR + "/synchrotrace.log"), shell=True)
        # TODO: is this needed for synchrotrace?
        subprocess.check_call("/bin/cat " + defs.ROOT_DIR +
                "/m5out/simout >> " + defs.LOG_DIR + "/synchrotrace.log", shell=True)

    def run(self):
        """
        Run the simulation
        Store statistics
        """
        self.run_simulation()

        # Collect the statistics
        filename = defs.ROOT_DIR + "/_OutSynchrotrace/stats.txt"
        self.stats = self.parse_stats(filename)
        os.remove(filename)

# NOTE: Synchrotrace needs to create a new trace evey time the number
# of cpu cores changes.
def main():
    sim = SynchroTraceSim(sys_config = {"cache_size" : 2048, "cpu_count" : 1})
    sim.run()

if __name__ == "__main__":
    main()
