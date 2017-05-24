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
from math import exp
from math import log

from enum import Enum

from mock_sim import MockSim

class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class Search_Algorithm(Enum):
    Elitist_Hill_Climber = 1
    Stochastic_Hill_Climber = 2
    A_Star = 3
    Simulated_Annealing = 4

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
        elif (self.algorithm == Search_Algorithm.Simulated_Annealing):
            self.search_simulated_annealing(search_state)


    def search_hill_climber(self, search_state):
        """
        Implements a hill climbing search algorithm given the starting seed
        configurations.
        """
        # TODO store direction we came from to cut down on superfluous searches

        # Initialize fitness scores for each configuration
        for i in range(self.num_search_parties):
            self.fitness_vals[i] = search_state.eval_fitness(self.sys_configs[i])

        converged = []

        for i in range(self.max_iterations):

            if (len(converged) == self.num_search_parties):
                return

            for j in range(self.num_search_parties):

                if (j in converged):
                    continue
                logging.info("Round {0}, Party: {1}".format(i, j))
                logging.info("Exploring node: {0}".format((self.fitness_vals[j], self.sys_configs[j])))
                # Each party will start a hill climbing search during each iteration
                new_sys_config, new_fitness = self.search_neighbors(self.sys_configs[j], self.fitness_vals[j], search_state)

                # TODO Implement plateau exploration
                if (new_sys_config == self.sys_configs[j]):
                    # Current nodes is a local max or min
                    logging.info("Search party {0} has converged.".format(j))
                    converged.append(j)
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
            
            # Greedy search on the neighboring search state. 
            next_config, next_fitness = self.get_best_sys_config(neighbor_configs, fitnesses)

            # If we've hit a plateau, terminate early.
            # TODO Do more informued plateau exploration
            if (next_fitness == current_fitness):
                next_config = sys_config
                next_fitness = current_fitness
        elif (self.algorithm == Search_Algorithm.Stochastic_Hill_Climber):
            # TODO choose neighbor with probability proportional to their
            # relative score
            next_config = sys_config
            next_fitness = fitnesses

        return next_config, next_fitness
    
    def search_simulated_annealing(self, search_state):

        converged = [] ## This keeps a track of the optimal values found in each search party
        # Setting up fitness values of seeds from each search party
        for i in range(self.num_search_parties):
            self.fitness_vals[i] = search_state.eval_fitness(self.sys_configs[i])
            converged.append({'fitness_val': 1000000, 'sys_config': ''})

        ## Initial temperature 
        t = 100
        # Absoute limit for minimum temperature 
        t_min = 5
        time = 1
        
        while t > t_min:
            for i in range(self.max_iterations):

                # if (len(converged) == self.num_search_parties):
                    # return

                for j in range(self.num_search_parties):

                    # if (j in converged):
                        # continue
                    # logging.info("Round {0}, Party: {1}".format(i, j))
                    # logging.info("Exploring node: {0}".format((self.fitness_vals[j], self.sys_configs[j])))
                    # Each party will start a hill climbing search during each iteration
                    new_sys_config, new_fitness, optimal_value = self.annealing_search(self.sys_configs[j], self.fitness_vals[j], search_state, t)
                    # logging.info('New_fitness: {0},\t Temperature: {1},\nNew_sys_config: {2} '.format(new_fitness, t, new_sys_config))

                    # Update convergence list with better node if found. 
                    if (optimal_value['fitness_val'] < converged[j]['fitness_val']):
                        converged[j] = optimal_value
                        logging.info("Found new optimal node at temperature {0} for search party {1}".format(t, j))
                    self.sys_configs[j] = new_sys_config
                    self.fitness_vals[j] = new_fitness
            
            ##logging.info("Round {0}, Party: {1}".format(i, j))
            # logging.info("Exploring node: {0}".format((self.fitness_vals[j], self.sys_configs[j])))
            logging.info('New_fitness: {0},\t Temperature: {1},\nNew_sys_config: {2} '.format(new_fitness, t, new_sys_config))
            t = t * 0.8 ## reducing the temperature 
        logging.info("Optimal Result: {0}".format(converged))

    def annealing_search(self, sys_config, fitness_val, search_state, temperature):
        # Generate possible neighbors
        neighbor_configs = self.gen_neighbors_randomly(sys_config)

        # Permute order of neighbors, just in case we're not searching through
        # all of them
        r.shuffle(neighbor_configs)

        fitnesses = []
        # This is used to keep a track of any peaks, in case SA strays from maxima
        most_optimum_value = {'fitness_val': -10, 'sys_config': ''}
        for n in neighbor_configs:
            # Evaluate each neighbor according to our evaluation function
            fitnesses.append(search_state.eval_fitness(n))

        # neighbor_configs.append(sys_config)
        # fitnesses.append(fitness_val)
        new_fitness = fitness_val # Sentinel value, as we want the lowest value 
        new_sys_config = sys_config

        for index, fitness in enumerate(fitnesses):
            acceptance = self.acceptance_probability(new_fitness, fitness, temperature)
            # logging.info('fitness values:{0}, acceptance: {1}'.format(fitness, acceptance))
            ## Neighboring node has a better fitness value, 
            ## hence, always accept it. 
            if new_fitness > fitness:
                new_fitness = fitness
                new_sys_config = neighbor_configs[index]
                most_optimum_value['fitness_val'] = new_fitness
                most_optimum_value['sys_config'] = new_sys_config
            
            ## This is the case where the neighboring node is 
            ## not as good as the current node. Only accept
            ## less optimal node if it has a high enough 
            ## acceptance probability. 
            elif acceptance < 1 and acceptance > r.random():
                new_fitness = fitness
                new_sys_config = neighbor_configs[index]
                
        return new_sys_config, new_fitness, most_optimum_value


    def gen_neighbors_randomly(self, sys_config):
        """
        Determine all possible neighbors of the given config but is done randomly
        instead of generating direct neighbors. This is done by choosing a value
        from the param range at random. 
        """

        neighbors = []
        for key in sys_config.keys():
            # Simply selects a random value for the given key within the param 
            # ranges
            config = copy.deepcopy(sys_config)
            current_index = self.param_ranges[key].index(sys_config[key])
            param_len = len(self.param_ranges[key])
            rand_index = current_index # sentinel value for the new random index
            while(rand_index == current_index):
                rand_index = r.randint(0, param_len-1)

            # logging.info('key: {2}, rand index: {0}, current index: {1}'.format(rand_index, current_index, key))

            config[key] = self.param_ranges[key][rand_index]
            neighbors.append(config)

        return neighbors
    
    def acceptance_probability(self, old_fitness, new_fitness, temperature):
        """
        This method determines whether a prticular sys_config is to be accepted
        or not. The idea with simulated annealing is to move to a better sys_config
        but not to get stuck in a plataeu by allowing the search to accept a slightly 
        worse state based on the acceptance probability to get out of a plateau. 
        """
        ## We are going to implement the standard notation for the acceptance 
        ## probability
        try:
            alpha = 1/exp(abs(old_fitness - new_fitness)/temperature)
        except OverflowError:
            alpha = float('inf')
        # logging.info('old: {}, new: {}, alpha: {}'.format(old_fitness, new_fitness, alpha))

        return alpha





