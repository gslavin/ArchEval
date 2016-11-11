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
import os

from enum import Enum

from mock_sim import MockSim

class Neighbor_Policy(Enum):
    Elitism = 1
    Stochastic = 2

def param_has_next(val, param_range):
    if (not val in param_range):
        raise ValueError("Current value not in range.")
    
    return param_range.index(val) < (len(param_range) - 1)

def param_next(val, param_range):
    return param_range[param_range.index(val) + 1]

def param_has_prev(val, param_range):
    if (not val in param_range):
        raise ValueError("Current value not in range.")

    return param_range.index(val) > 0

def param_prev(val, param_range):
    return param_range[param_range.index(val) - 1]

default_param_ranges = {
                       "cpu_count" : list(range(1, 9)),
                       "cpu_frequency" : list(map(lambda x: x * 10**9, range(1, 8))),
                       "cache_size" : list(map(lambda x: 2**x, range(10, 17))),
                       }


class DSE_searcher:
    """
    Wrapper class for the design space exploration search.
    Uses the simulation wrappers to a run a variety of simulations
    """

    def __init__(self, user_constraints, param_ranges, max_iterations = 20, num_search_parties = 1):

        if (max_iterations < 1):
            raise ValueError("Max iterations must be strictly positive.")

        if (num_search_parties < 1):
            raise ValueError("Number of search parties must be strictly positive.")

        if (not isinstance(param_ranges, dict)):
            raise ValueError("Parameter ranges takes the form of a dictionary.")

        self.max_iterations = max_iterations
        self.num_search_parties = num_search_parties
        self.user_constraints = user_constraints

        # Default to elitism policy - best of N search directions is chosen
        self.policy = Neighbor_Policy.Elitism
        # Default to searching all dimensions to determine best gradient. 
        # (-1 denotes all directions. Range: {-1} ^ [1, D]
        # TODO: implment this feature (Eric Rock)
        self.search_directions = -1

        self.sys_configs = []
        self.fitness_vals = []

        # Store configuration parameters and their ranges
        self.param_ranges = copy.deepcopy(default_param_ranges)
        for key in param_ranges.keys():
            self.param_ranges[key] = param_ranges[key]

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

        # Create permuation of all parameters
        self.shuffled_params = copy.deepcopy(self.param_ranges)
        for key in self.shuffled_params.keys():
            # Create a random permutation of the parameter values
            r.shuffle(self.shuffled_params[key])

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

    def gen_rand_config(self):
        """
        Generate a random configuration within the space of input parameters
        """

        # TODO take into account user constraints?
        config = {}
        for key in self.shuffled_params.keys():
            # Assign the first element of the shuffled list to this config
            config[key] = self.shuffled_params[key][0]
            # Shift the contents of the shuffled list
            self.shuffled_params[key].append(self.shuffled_params[key].pop(0))

        return config

    def search(self, eval_sys_config):
        """
        Top level search
        Each search party starts at its random starting point
        Neighbors around the starting point are tested
        A direction is chosen to continue the search
        """
        
        # TODO store direction we came from to cut down on superfluous searches

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
        for key in sys_config.keys():
            # If the parameter has a 'next' element, add a neighbor of the next
            # element
            if (param_has_next(sys_config[key], self.param_ranges[key])):
                config = copy.deepcopy(sys_config)
                config[key] = param_next(sys_config[key], self.param_ranges[key])
                neighbors.append(config)

            # If the parameter has a 'prev' element, add a neighbor of the
            # previous element
            if (param_has_prev(sys_config[key], self.param_ranges[key])):
                config = copy.deepcopy(sys_config)
                config[key] = param_prev(sys_config[key], self.param_ranges[key])
                neighbors.append(config)

        return neighbors

    def get_best_sys_config(self, sys_configs, fitnesses):
        best = min(zip(sys_configs, fitnesses),
                   key = lambda x: x[1])
        if ("ArchEval_DBG" in os.environ and os.environ["ArchEval_DBG"] == "1"):
            print(best)

        return best

    def search_neighbors(self, sys_config, current_fitness, eval_sys_config):
        """
        Searches neighbor nodes to see if they provide a better score
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
            # Evaluate each neighbor according to our evaluation function
            fitnesses.append(eval_sys_config(n))

        neighbor_configs.append(sys_config)
        fitnesses.append(current_fitness)
        if (self.policy == Neighbor_Policy.Elitism):
            next_config, next_fitness = self.get_best_sys_config(neighbor_configs, fitnesses)
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
    search = DSE_searcher(user_constraints = None, param_ranges = {})
    search.search(mock_eval_sys_config)

if __name__ == "__main__":
    main()
