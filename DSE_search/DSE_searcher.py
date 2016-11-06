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
import copy

from enum import Enum

from mock_sim import MockSim

class Neighbor_Policy(Enum):
    Elitism = 1
    Stochastic = 2


class DSE_searcher:
    """
    Wrapper class for the design space exploration search.
    Uses the simulation wrappers to a run a variety of simulations
    """

    def __init__(self, user_constraints, max_iterations = 20, num_search_parties = 1):

        self.max_iterations = max_iterations
        self.num_search_parties = num_search_parties
        self.user_constraints = user_constraints

        # Default to elitism policy - best of N search directions is chosen
        self.policy = Neighbor_Policy.Elitism
        # Default to searching all dimensions to determine best gradient. 
        # (-1 denotes all directions. Range: {-1} ^ [1, D]
        self.search_directions = -1

        self.sys_configs = []
        self.fitness_vals = []

        # Store configuration parameters and their ranges
        self.params = []
        self.params.append(("cpu_count", list(range(1, 8))))
        self.params.append(("cpu_frequency", list(map(lambda x: x * 10**9, range(1, 7)))))
        self.params.append(("cache_size", list(map(lambda x: 2**x, range(10, 17)))))

        # Generate the intial config for each search party
        self.sys_configs = list(it.islice(self.gen_inital_sys_config(),
                                                  self.num_search_parties))

        for _ in self.sys_configs:
            self.fitness_vals.append(0)

    def gen_inital_sys_config(self):
        """
        Generates a stream of non-repeating system configuration
        based on the user constraints
        """
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

        # Create permuation of all parameters
        self.shuffled_params = copy.deepcopy(self.params)
        for param in self.shuffled_params:
            # Create a random permutation of the parameter values
            r.shuffle(param[1])

        config = {}
        for i in range(0, len(self.shuffled_params)):
            # Config Format: map - name -> (value, [range])
            config[self.shuffled_params[i][0]] = (self.shuffled_params[i][1][0], self.params[i][1])
            # Shift the contents of the parameter list
            param[1].append(param[1].pop())

        return config


    def search(self, eval_sys_config):
        """
        Top level search
        Each search party starts at its random starting point
        Neighbors around the starting point are tested
        The best neighbor is chosen
        """

        # Initialize fitness scores for each configuration
        for i in range(self.num_search_parties):
            self.fitness_vals[i] = eval_sys_config(self.sys_configs[i])

        for _ in range(self.max_iterations):
            for i in range(self.num_search_parties):
                # Each party will start a hill climbing search during each iteration
                new_sys_config, new_fitness = self.search_neighbors(self.sys_configs[i], self.fitness_vals[i], eval_sys_config)

                # TODO Implement plateau exploration
                if (new_sys_config == self.sys_configs[i]):
                    # Current nodes is a local max or min
                    pass
                self.sys_configs[i] = new_sys_config
                self.fitness_vals[i] = new_fitness

    def gen_neighbors(self, sys_config):
        """
        Determine all possible neighbors of the given config
        """

        neighbors = []

        for param in sys_config:

            # If the parameter has a 'next' element, add a neighbor of the next
            # element
            if (sys_config[param][1].index(sys_config[param][0]) < len(sys_config[param][1]) - 1):
                config = copy.deepcopy(sys_config)
                config[param] = (sys_config[param][1][sys_config[param][1].index(sys_config[param][0]) + 1], sys_config[param][1])
                neighbors.append(config)

            # If the parameter has a 'prev' element, add a neighbor of the
            # previous element
            if (sys_config[param][1].index(sys_config[param][0]) != 0):
                config = copy.deepcopy(sys_config)
                config[param] = (sys_config[param][1][sys_config[param][1].index(sys_config[param][0]) - 1], sys_config[param][1])
                neighbors.append(config)

        return neighbors

    def search_neighbors(self, sys_config, current_fitness, eval_sys_config):
        """
        Searches neighbor nodes to see if they provide a better score
        Uses simulation wrappers
        """
        if (self.search_directions == -1):
            search_dirs = len(sys_config)
        elif (self.search_directions == 0):
            self.search_directions = 1
        else:
            search_dirs = max(len(sys_config), self.search_directions)

        # Generate possible neighbors
        neighbor_configs = self.gen_neighbors(sys_config)
        
        # Permute order of neighbors, just in case we're not searching through
        # all of them
        r.shuffle(neighbor_configs)

        fitnesses = []
        for n in neighbor_configs:
            # Run simulations (via simulation wrappers)
            # score simulation results according to user constraints
            fitnesses.append(eval_sys_config(n))

        sys_configs = neighbor_configs.append(sys_config)
        fitnesses.append(current_fitness)
        if (self.policy == Neighbor_Policy.Elitism):
            # TODO choose best scoring neighbor
            best = min(zip(neighbor_configs, fitnesses), 
                key = lambda x: x[1])
            print(best)
            next_config = best[0]
            next_fitness = best[1]
        elif (self.policy == Neighbor.Stochastic):
            # TODO choose neighbor with probability proportional to their
            # relative score
            next_config = sys_config
            next_fitness = fitnesses

        return next_config, next_fitness

def eval_stats(stats):
    """
    Basic function to minimize
    """
    #TODO:  How to calibrate parameters?
    a = 10e9
    b = 1/(1048576)
    result = a*stats["execution time (s)"] + b*stats["Area (mm2)"]
    
    return result

def mock_eval_sys_config(sys_config):
    """
    Runs the configuration through the mock simulation
    """
    mock_sim = MockSim(sys_config)

    mock_sim.run()
    return eval_stats(mock_sim.stats)

def main():
    search = DSE_searcher(None)
    search.search(mock_eval_sys_config)

if __name__ == "__main__":
    main()
