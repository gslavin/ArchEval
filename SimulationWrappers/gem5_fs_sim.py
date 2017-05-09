#!/usr/bin/env python3

from simulation_wrapper import SimWrap

import string
import re
import json
import subprocess
import defs
import os

from gem5_sim import nested_stats_insert
from gem5_sim import gem5_parse_value
from gem5_sim import gem5_parse_freq
from gem5_sim import gem5_parse_cache

config_defaults = { "cpu_count": 1,\
                    "cpu_frequency": 9000000,\
                    "cache_size": 1024,\
                    "l1d_assoc": 2,\
                    "l1i_size": 1024,\
                    "l1i_assoc": 2,\
                    "num-l2caches": 1,\
                    "l2_size": 1024,\
                    "l2_assoc": 2,\
                  }

valid_sys_config_params = [ "cpu_count",\
                            "cpu_frequency",\
                            "cache_size",\
                            "l1d_assoc",\
                            "l1i_size",\
                            "l1i_assoc",\
                            "num-l2caches",\
                            "l2_size",\
                            "l2_assoc"\
                          ]

class Gem5FSSim(SimWrap):
    """
    self.config
        simulation configuration
    self.stats ## dict of information
        simulation results
    """

    def __init__(self, benchmark, options, kernel, disk_image, sys_config = config_defaults):
        """
        Pass in dictionary of simulation parameters
        Store configuration of simulation
        """

        if (len(defs.GEM5_DIR) == 0):
            raise ValueError("Please update Gem5 directory in defs.py.")

        # TODO check that kernel exists
        # TODO check that disk image exists

        self.config = {}
        self.set_config(sys_config)
        self.benchmark = benchmark
        self.options = options
        self.kernel = kernel
        self.disk_image = disk_image

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
        # TODO verify that checkpoint dir for cpu cores value exists

        subprocess.check_call("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15} >> {16}".format(\
                                defs.GEM5_DIR + "/build/X86_MOESI_hammer/gem5.opt", \
                                "--stats-file=" + defs.ROOT_DIR + "/stats.txt", \
                                "-r", \
                                defs.GEM5_DIR + "/configs/example/fs.py", \
                                "--kernel=" + self.kernel, \
                                "--disk-image=" + self.disk_image, \
                                """--cpu-type="timing" """, \
                                " --num-cpus=" + str(self.config["cpu_count"]), \
                                "--l1d_size=" + gem5_parse_cache(self.config["cache_size"]), \
                                "--l1d_assoc=" + str(self.config["l1d_assoc"]), \
                                "--l1i_size=" + gem5_parse_cache(self.config["l1i_size"]), \
                                "--l1i_assoc=" + str(self.config["l1i_assoc"]), \
                                "--num-l2caches=" + str(self.config["num-l2caches"]), \
                                "--l2_size=" + gem5_parse_cache(self.config["l2_size"]), \
                                "--l2_assoc=" + str(self.config["l2_assoc"]), \
                                "--script=" + self.benchmark, \
                                defs.LOG_DIR + "/gem5.log"), shell=True)
        subprocess.check_call("/bin/cat " + defs.ROOT_DIR + "/m5out/system.pc.com_1.terminal >> " + defs.LOG_DIR + "/gem5.log", shell=True)
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
    sim = Gem5FSSim("/home/solisknight/tmp/blackscholes_8c_simsmall.rcS", \
                    "", \
                    "/dist/m5/system/binaries/x86_64-vmlinux-2.6.22.9.smp", \
                    "/dist/m5/system/disks/x86root.img")
    sim.run()
    print(sim.stats_to_json())

if __name__ == "__main__":
    main()
