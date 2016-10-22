#
# ECE49X - Senior Design
# Eric Rock, George Slavin, Avik Bag
# ArchEval
#
# Design Space Exploration Tool
# Stochastic Hill Climbing Algorithm
#

import string
import sys

import random


class DSE_searcher:

    def __init__( self, search_params, max_num_generations = 10, search_parties = 2 ):
        self.search_params = search_params
        self.search_state = []


        self.max_num_generations = max_num_generations
        self.search_parties = search_parties

        for i in range(self.search_parties):
            self.search_state.append([])

            for param in search_params: 
                if (param.size() == 0)
                    continue
                else if (param.size() == 1)
                    i = 0
                else
                    i = randint(1, param.size() - 1)
                
                self.search_state[i].append( (param, i) );


    def search( self ):
        # TODO: Determine how to establish initial target values to optimize
        # TODO: Determine interface to start simulations, retrieve results


        
