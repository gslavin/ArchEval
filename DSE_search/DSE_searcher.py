#!/usr/bin/python3

#
# ECE49X - Senior Design
# Eric Rock, George Slavin, Avik Bag
# ArchEval
#
# Design Space Exploration Tool
# Stochastic Hill Climbing Algorithm
#

import logging
import itertools as it
import random as r
import copy
import os

from enum import Enum

from mock_sim import MockSim

class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class Search_Algorithm(Enum):
    Elitist_Hill_Climber = 1
    Stochastic_Hill_Climber = 2
    A_Star = 3

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

def seed_dist(A, B):
    """
    Calculates the L1 distance between two seeds
    """
    ret = 0;
    for key in A.keys():
        if (not key in B.keys()):
            raise ValueError("Expected key not present.")

        ret += abs(A[key] - B[key])
    return ret

def seed_repel(A, B, ranges, alpha, min_dist):
    """
    Simulates repulsion between two seeds by randomly shifting indices which
    have distance < min_dist from each other with probability alpha.
    """
    if (seed_dist(A, B) < min_dist):
        for key in A.keys():
            # Repel a feature at a learning rate of alpha
            if (r.random() > alpha):
                continue;
            # If this feature is being repelled, push each value away from each
            # other within the range.
            if (A[key] < B[key]):
                if (A[key] > 0):
                    A[key] -= 1
                if (B[key] < (len(ranges[key]) - 1)):
                    B[key] += 1
            else:
                if (B[key] > 0):
                    B[key] -= 1
                if (A[key] < (len(ranges[key]) - 1)):
                    A[key] += 1


default_param_ranges = {
                       "cpu_count" : list(range(1, 9)),
                       "cpu_frequency" : list(map(lambda x: x * 10**9, range(1, 8))),
                       "cache_size" : list(map(lambda x: 2**x, range(11, 17))),
                       }


class DSE_searcher:
    """
    Wrapper class for the design space exploration search.
    Uses the simulation wrappers to a run a variety of simulations
    """

    def __init__(self, param_ranges, max_iterations = 20, num_search_parties = 1):
        """
        public functions:
        - search()
            Finds a locally optimal system configuration
        """

        if (max_iterations < 1):
            raise ValueError("Max iterations must be strictly positive.")

        if (num_search_parties < 1):
            raise ValueError("Number of search parties must be strictly positive.")

        if (not isinstance(param_ranges, dict)):
            raise ValueError("Parameter ranges takes the form of a dictionary.")

        self.max_iterations = max_iterations
        self.num_search_parties = num_search_parties

        # Default to elitism policy - best of N search directions is chosen
        self.algorithm = Search_Algorithm.Elitist_Hill_Climber
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

        self.sys_configs = self.gen_search_parties(self.num_search_parties);

        for _ in self.sys_configs:
            self.fitness_vals.append(0)

    def gen_search_parties(self, N):
        """
        Generates a list of system configurations which are some (configurable)
        distance from each other.
        """
        # Repelling rate
        alpha = 0.5

        # Minimum distance within which repelling will occur
        min_dist = 2

        # num iterations
        iterations = 10000 * N

        parties = [];

        # Generate seeds of random indices within each parameter range
        for i in range(0, N):
            parties.append({})
            for key in self.param_ranges.keys():
                parties[i][key] = r.randint(0, len(self.param_ranges[key]) - 1)

        # Repel seeds from each other randomly for a set number of iterations
        if (N > 1):
            for i in range(0, iterations):
                a = r.randint(0, N - 1)
                b = r.randint(0, N - 1)
                while (a == b):
                    b = r.randint(0, N - 1)

                seed_repel(parties[a], parties[b], self.param_ranges, alpha, min_dist)

        # Convert seed indices into actual sys configs
        configs = [];
        for i in range(0, N):
            configs.append({})
            for key in parties[i].keys():
                configs[i][key] = self.param_ranges[key][parties[i][key]]
            logging.info("initial config{0}: {1}".format(i, configs[i]))

        return configs

    def search(self, search_state):
        """
        Top level search
        Directs search according to chosen search algorithm.
        """

        if ((self.algorithm == Search_Algorithm.Elitist_Hill_Climber) or
            (self.algorithm == Search_Algorithm.Stochastic_Hill_Climber)):
            self.search_hill_climber(search_state)
        elif (self.algorithm == Search_Algorithm.A_Star):
            self.search_a_star(search_state)


    def search_hill_climber(self, search_state):
        """
        Implements a hill climbing search algorithm given the starting seed
        configurations.
        """
        # TODO store direction we came from to cut down on superfluous searches

        # Initialize fitness scores for each configuration
        for i in range(self.num_search_parties):
            self.fitness_vals[i] = search_state.eval_fitness(self.sys_configs[i])

        for i in range(self.max_iterations):
            for j in range(self.num_search_parties):
                logging.info("Round {0}, Party: {1}".format(i, j))
                # Each party will start a hill climbing search during each iteration
                new_sys_config, new_fitness = self.search_neighbors(self.sys_configs[j], self.fitness_vals[j], search_state)

                # TODO Implement plateau exploration
                if (new_sys_config == self.sys_configs[j]):
                    # Current nodes is a local max or min
                    pass
                self.sys_configs[j] = new_sys_config
                self.fitness_vals[j] = new_fitness


    def search_a_star(self, search_state):
        """
        Implements A* search algorithm from the first seed configuration given
        for an exhaustive search of the search space.
        """
        explored = set()
        frontier = []

        frontier.append((search_state.eval_fitness(self.sys_configs[0]), self.sys_configs[0]))

        best = frontier[0]


        while (len(frontier) > 0):
            frontier.sort(key = lambda x: x[0], reverse=True)
            (fitness, sys_config) = frontier.pop()

            logging.info("Exploring node: {0}".format((fitness, sys_config)))

            if (fitness < best[0]):
                best = (fitness, sys_config)

            neighbors = self.gen_neighbors(sys_config)

            for config in neighbors:
                if (not hashabledict(config) in explored):
                    frontier.append( (search_state.eval_fitness(config), config) )
                    explored.add(hashabledict(config))


        logging.info("Best config: {0}".format(best))


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
        logging.info("Best config: {0}".format(best))

        return best

    def search_neighbors(self, sys_config, current_fitness, search_state):
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
            fitnesses.append(search_state.eval_fitness(n))

        neighbor_configs.append(sys_config)
        fitnesses.append(current_fitness)
        if (self.algorithm == Search_Algorithm.Elitist_Hill_Climber):
            next_config, next_fitness = self.get_best_sys_config(neighbor_configs, fitnesses)
        elif (self.algorithm == Search_Algorithm.Stochastic_Hill_Climber):
            # TODO choose neighbor with probability proportional to their
            # relative score
            next_config = sys_config
            next_fitness = fitnesses

        return next_config, next_fitness
