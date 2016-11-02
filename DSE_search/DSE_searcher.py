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

from enum import Enum

class Neighbor_Policy(Enum):
    Elitism = 1
    Stochastic = 2


class DSE_searcher:
    """
    Wrapper class for the design space exploration search.
    Uses the simulation wrappers to a run a variety of simulations
    """

    def __init__(self, user_constraints, max_iterations = 10, num_search_parties = 2):

        self.max_iterations = max_iterations
        self.num_search_parties = num_search_parties
        self.user_constraints = user_constraints

        # Default to elitism policy - best of N search directions is chosen
        self.policy = Neighbor_Policy.Elitism
        # Default to searching all dimensions to determine best gradient. (-1
        # denotes all directions. Range: {-1} ^ [1, D]
        self.search_directions = -1

        self.sys_configs = []
        self.fitness_vals = []

        # Generate the intial config for each search party
        self.sys_configs = list(it.islice(self.gen_inital_sys_config(),
                                                  self.num_search_parties))

        for _ in self.sys_configs:
            self.fitness_vals.append(0)

        print(self.sys_configs)

    def gen_inital_sys_config(self):
        """
        Generates a stream of non-repeating system configuration
        based on the user constraints
        """
        # TODO: Use single random permuation of parameters instead of n random
        # permutations in order to promote greater distance between initial
        # seeds

        #
        # TODO: FIXME This algorithm will loop infinitely if all permutations
        # have been returned already
        #
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


    def search(self, evaluate_fn):
        """
        Top level search
        Each search party starts at its random starting point
        Neighbors around the starting point are tested
        The best neighbor is chosen
        """

        # Initialize fitness scores for each configuration
        for i in range(self.num_search_parties):
            self.fitness_vals[i] = evaluate_fn(self.sys_configs[i])

        for _ in range(self.max_iterations):
            for i in range(self.num_search_parties):
                # Each party will start a hill climbing search during each iteration
                new_sys_config, new_fitness = self.search_neighbors(self.sys_configs[i], self.fitness_vals[i], evaluate_fn)

                # TODO Implement plateau exploration
                if (new_sys_config == self.sys_configs[i]):
                    # Current nodes is a local max or min
                    pass
                self.sys_configs[i] = new_sys_config
                self.fitness_vals[i] = new_fitness

    def search_neighbors(self, sys_config, fitness, evaluate_fn):
        """
        Searches neighbor nodes to see if thye provide a better score
        Uses simulation wrappers
        """
        if (self.search_directions == -1):
            search_dirs = len(sys_config)
        elif (self.search_directions == 0):
            self.search_directions = 1
        else:
            search_dirs = max(len(sys_config), self.search_directions)

        # Generate possible neighbors
        neighbors = []
        fitness = []
        for param in sys_config:
            neighbors.append(sys_config)
            # TODO determine how to vary search parameters generally
            fitness.append(0)

        
        # Permute order of neighbors, just in case we're not searching through
        # all of them
        r.shuffle(neighbors)

        for i in range(len(neighbors)):
            fitness[i] = evaluate_fn(neighbors[i])
            # Run simulations (via simulation wrappers)
            # score simulation results according to user constraints
            pass

        if (self.policy == Neighbor_Policy.Elitism):
            # TODO choose best scoring neighbor
            next_config = sys_config
            next_fitness = fitness
        elif (self.policy == Neighbor.Stochastic):
            # TODO choose neighbor with probability proportional to their
            # relative score
            next_config = sys_config
            next_fitness = fitness

        return next_config, next_fitness


def main():
    search = DSE_searcher(None)
    search.search(lambda config: 0)

if __name__ == "__main__":
    main()
