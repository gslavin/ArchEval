#!/usr/bin/env python3

import datetime
import logging
import unittest
import os
import defs

from DSE_searcher import DSE_searcher
from DSE_searcher import Search_Algorithm
from DSE_search_state import *
from mock_sim import MockSim
from test_utils import log_name

default_benchmark = defs.ROOT_DIR + "/Tests/test-progs/random_access/random_access"
default_options = "1000"

def generate_job_output(sys_configs, search_state):
    filename = defs.LOG_DIR + '/' + 'gem5_job_output{:%Y_%m_%d-%H:%M:%S}.json'.format(datetime.datetime.now())
    with open(filename, "w") as result_file:
            output = search_state.generate_job_output(sys_configs)
            result_file.write(output)
            logging.info(output)

class TestSearcher(unittest.TestCase):
    @log_name
    def test_defaults(self):
        s = DSE_searcher({})
        search_state = MockSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_more_seeds(self):
        s = DSE_searcher({}, num_search_parties = 2)
        search_state = MockSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_min_start(self):
        s = DSE_searcher({})
        s.sys_configs = [{"cache_size": 2**11, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        search_state = MockSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_max_start(self):
        s = DSE_searcher({})
        s.sys_configs = [{"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}]
        search_state = MockSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_invalid_args(self):
        s = DSE_searcher({})

        with self.assertRaises(ValueError):
            s = DSE_searcher([])

        with self.assertRaises(ValueError):
            s = DSE_searcher({}, num_search_parties = -1)

        with self.assertRaises(ValueError):
            s = DSE_searcher({}, max_iterations = -1)

        with self.assertRaises(ValueError):
            s = DSE_searcher(param_ranges = [1,2,3])

    # TODO: fix stat_output for multiple search parties
    @log_name
    def test_stat_output(self):
        s = DSE_searcher(param_ranges = {}, num_search_parties=1)
        mock_search_state = MockSearchState({}, {}, default_benchmark, default_options)
        s.search(mock_search_state)

        generate_job_output(s.sys_configs, mock_search_state)

    @log_name
    def test_large_num_seeds(self):
        s = DSE_searcher({}, num_search_parties=10)
        search_state = MockSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_A_star(self):
        modified_param_ranges = {
                                "cpu_count" : list(range(1, 4)),
                                "cpu_frequency" : list(map(lambda x: x * 10**9, range(1, 4))),
                                "cache_size" : list(map(lambda x: 2**x, range(11, 13))),
                                }
        s = DSE_searcher(modified_param_ranges, num_search_parties=1)
        s.algorithm = Search_Algorithm.A_Star
        search_state = MockSearchState({}, {}, default_benchmark, default_options)

    def test_embedded_heuristic(self):
        s = DSE_searcher({})
        s.sys_configs = [{"cache_size": 2**16, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        search_state = EmbeddedSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_balanced_heuristic(self):
        s = DSE_searcher({})
        s.sys_configs = [{"cache_size": 2**11, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        search_state = BalancedSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

    @log_name
    def test_high_performance_heuristic(self):
        s = DSE_searcher({})
        s.sys_configs = [{"cache_size": 2**11, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        search_state = HighPerformanceSearchState({}, {}, default_benchmark, default_options)
        s.search(search_state)

class TestSearcherGem5(unittest.TestCase):
    @log_name
    def test_defaults(self):
        modified_param_ranges = {
                                "cpu_count" : list(range(1, 4)),
                                "cpu_frequency" : list(map(lambda x: x * 10**9, range(1, 4))),
                                "cache_size" : list(map(lambda x: 2**x, range(11, 14))),
                                }


        s = DSE_searcher(modified_param_ranges)
        #s.sys_configs = [{"cache_size": 2**10, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        search_state = FullSearchState({}, default_benchmark, default_options)
        s.search(search_state)
        #generate_job_output(s.sys_configs, search_state)


    def test_A_star(self):
        modified_param_ranges = {
                                "cpu_count" : list(range(1, 3)),
                                "cpu_frequency" : list(map(lambda x: x * 10**9, range(1, 3))),
                                "cache_size" : list(map(lambda x: 2**x, range(11, 13))),
                                }

        s = DSE_searcher(modified_param_ranges)
        s.algorithm = Search_Algorithm.A_Star
        search_state = FullSearchState({}, default_benchmark, "100")
        s.search(search_state)
        #generate_job_output(s.sys_configs, search_state)

class TestSearcherSynchroTrace(unittest.TestCase):
    @log_name
    def test_defaults(self):
        modified_param_ranges = {
                                "cpu_count" : list(map(lambda x: 2**x, range(0, 4))),
                                "cpu_frequency" : list(map(lambda x: x * 10**9, range(1, 4))),
                                "cache_size" : list(map(lambda x: 2**x, range(11, 14))),
                                }
        s = DSE_searcher(modified_param_ranges)
        search_state = FastFullSearchState({}, default_benchmark, default_options)
        s.search(search_state)
        #generate_job_output(s.sys_configs, search_state)

class TestMcPatSearcher(unittest.TestCase):
    @log_name
    def test_defaults(self):
        s = DSE_searcher({})
        search_state = McPatSearchState({}, default_benchmark, default_options)
        s.search(search_state)

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name = script_name.split(".")[0]
    logging.basicConfig(filename=defs.LOG_DIR + '/{}.log'.format(script_name), level=logging.INFO)
    logging.info("START {} TESTS: {:%Y-%m-%d %H:%M:%S}".format(script_name, datetime.datetime.now()))
    unittest.main()
    logging.info("END {} TESTS".format(script_name))
