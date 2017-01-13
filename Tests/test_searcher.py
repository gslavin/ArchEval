#!/usr/bin/python3

import datetime
import logging
import unittest
import os
import defs

from DSE_searcher import DSE_searcher
from DSE_search_state import MockSearchState
from mock_sim import MockSim
from test_utils import log_name

class TestSearcher(unittest.TestCase):
    @log_name
    def test_defaults(self):
        s = DSE_searcher(None, {})
        search_state = MockSearchState({}, {})
        s.search(search_state)

    @log_name
    def test_more_seeds(self):
        s = DSE_searcher(None, {}, num_search_parties = 2)
        search_state = MockSearchState({}, {})
        s.search(search_state)

    @log_name
    def test_min_start(self):
        s = DSE_searcher(None, {})
        search_state = MockSearchState({}, {})
        s.search(search_state)
        
    @log_name
    def test_max_start(self):
        s = DSE_searcher(None, {})
        search_state = MockSearchState({}, {})
        s.search(search_state)

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
    def test_stat_output(self):
        s = DSE_searcher(user_constraints = None, param_ranges = {}, num_search_parties=2)
        mock_search_state = MockSearchState({}, {})
        s.search(mock_search_state)
        for config in s.sys_configs:
            logging.info(mock_search_state.generate_job_output(config))


    @log_name
    def test_large_num_seeds(self):
        s = DSE_searcher(None, {}, num_search_parties=100)
        search_state = MockSearchState({}, {})
        s.search(search_state)
        

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name = script_name.split(".")[0]
    logging.basicConfig(filename=defs.LOG_DIR + '/{}.log'.format(script_name), level=logging.INFO)
    logging.info("START {} TESTS: {:%Y-%m-%d %H:%M:%S}".format(script_name, datetime.datetime.now()))
    unittest.main()
    logging.info("END {} TESTS".format(script_name))
