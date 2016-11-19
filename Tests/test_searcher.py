#!/usr/bin/python3

import datetime
import logging
import unittest
import os
import defs

from DSE_searcher import DSE_searcher
from mock_sim import MockSim
from test_utils import log_name

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

class TestSearcher(unittest.TestCase):
    @log_name
    def test_defaults(self):
        s = DSE_searcher(None, {})
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])

    @log_name
    def test_more_seeds(self):
        s = DSE_searcher(None, {}, num_search_parties = 2)
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])

    @log_name
    def test_min_start(self):
        s = DSE_searcher(None, {})
        s.sys_configs = [{"cache_size": 2**10, "cpu_frequency" : 1e9, "cpu_count" : 1}]
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])
        
    @log_name
    def test_max_start(self):
        s = DSE_searcher(None, {})
        s.sys_configs = [{"cache_size": 2**16, "cpu_frequency" : 7e9, "cpu_count" : 8}]
        s.search(lambda x : - x["cache_size"] - x["cpu_frequency"] - x["cpu_count"])

    @log_name
    def test_invalid_args(self):
        s = DSE_searcher(None, {})

        with self.assertRaises(ValueError):
            s = DSE_searcher(None, [])

        with self.assertRaises(ValueError):
            s = DSE_searcher(None, {}, num_search_parties = -1)

        with self.assertRaises(ValueError):
            s = DSE_searcher(None, {}, max_iterations = -1)

        with self.assertRaises(ValueError):
            s = DSE_searcher(None, param_ranges = [1,2,3])

    @log_name
    def test_mock_sim(self):
        search = DSE_searcher(user_constraints = None, param_ranges = {})
        search.search(mock_eval_sys_config)

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name = script_name.split(".")[0]
    logging.basicConfig(filename=defs.LOG_DIR + '/{}.log'.format(script_name), level=logging.INFO)
    logging.info("START {} TESTS: {:%Y-%m-%d %H:%M:%S}".format(script_name, datetime.datetime.now()))
    unittest.main()
    logging.info("END {} TESTS".format(script_name))
