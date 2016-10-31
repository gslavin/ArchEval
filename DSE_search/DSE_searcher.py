#!/usr/bin/python3

#
# ECE49X - Senior Design
# Eric Rock, George Slavin, Avik Bag
# ArchEval
#
# Design Space Exploration Tool
# Stochastic Hill Climbing Algorithm
#

import itertools as it
import random as r


class DSE_searcher:
    """
    Wrapper class for the design space exploration search.
    Uses the simulation wrappers to a run a variety of simulations
    """

    def __init__(self, user_constraints, max_iterations = 10, num_search_parties = 2):

        self.max_iterations = max_iterations
        self.num_search_parties = num_search_parties
        self.user_constraints = user_constraints
        self.sys_configs = []

        # Generate the intial config for each search party
        self.sys_configs = list(it.islice(self.gen_inital_sys_config(),
                                                  self.num_search_parties))

        print(self.sys_configs)

    def gen_inital_sys_config(self):
        """
        Generates a stream of non-repeating system configuration
        based on the user constraints
        """
        prev_configs = []
        while True:
            config = self.gen_rand_config()
            while config in prev_configs:
               config = self.gen_rand_config()
            prev_configs.append(config)
            yield config

    # TODO: Determine how to establish initial target values to optimize
    def gen_rand_config(self):
        """
        Use the user constraints to generate a random configuration
        """
        config = {}
        config["cpu_count"] = r.randint(1, 8)
        config["cpu_frequency"] = r.randint(1,7)*1000000000
        config["cache_size"] =  2**(r.randint(15,25))
        return config


    def search(self):
        """
        Top level search
        Each search party starts at its random starting point
        Neighbors around the starting point are tested
        The best neighbor is chosen
        """
        for _ in range(self.max_iterations):
            for i in range(self.num_search_parties):
                # Each party will start a hill climbing search during each iteration
                new_sys_config = self.search_neighbors(self.sys_configs[i])
                if (new_sys_config == self.sys_configs[i]):
                    # Current nodes is a local max or min
                    pass
                self.sys_configs[i] = new_sys_config

    def search_neighbors(self, sys_config):
        """
        Searches neighbor nodes to see if thye provide a better score
        Uses simulation wrappers
        """
        # Generate possible neighbors
        neighbors = []
        for n in neighbors:
            # Run simulations (via simulation wrappers)
            # score simulation results according to user constraints
            pass

        # Choose best scoring neighbor

        return sys_config


def main():
    search = DSE_searcher(None)
    search.search()

if __name__ == "__main__":
    main()
